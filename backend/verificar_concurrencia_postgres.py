"""Prueba explícita en un esquema desechable de PostgreSQL; nunca usa tablas del CRM.

Ejecutar con --ejecutar. No llama al proveedor de IA. El esquema se crea con nombre
aleatorio propio y se retira en finally; no acepta nombres de esquema por parámetro.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from threading import Barrier, local
from uuid import uuid4


def verificar():
    if not __debug__:
        raise RuntimeError('Ejecuta sin -O: las comprobaciones deben permanecer activas.')
    import database
    import models
    import tareas_chat
    from consultas_mobilita import Consulta, ejecutar_consulta
    from fastapi import HTTPException
    from sqlalchemy import event, text
    from sqlalchemy.schema import CreateSchema, DropSchema
    from sqlalchemy.orm import Session

    if database.engine.dialect.name != 'postgresql':
        raise ValueError('Esta prueba requiere PostgreSQL.')
    esquema='qa_mobilita_'+uuid4().hex
    if not re.fullmatch(r'qa_mobilita_[0-9a-f]{32}', esquema):
        raise ValueError('Nombre de prueba inválido.')
    motor=database.engine.execution_options(schema_translate_map={None:esquema})
    tablas=[models.Usuario.__table__,models.Lead.__table__,models.Tarea.__table__,
            models.Auditoria.__table__,models.PropuestaTareaChat.__table__]
    creado=False
    resultado={'fecha':datetime.now(timezone.utc).isoformat(), 'motor':'PostgreSQL',
               'datos':'Ficticios en esquema aislado', 'llamadas_ia':0, 'casos':{}}
    try:
        with database.engine.begin() as conexion:
            conexion.execute(CreateSchema(esquema)); creado=True
        models.Base.metadata.create_all(motor,tables=tablas)
        with Session(motor) as db:
            usuario=models.Usuario(nombre='Ejecutivo temporal',email='qa@example.test',rol='ejecutivo',password_hash='no-utilizable')
            lead=models.Lead(nombre='Cliente temporal',email='cliente@example.test',estado='Nuevo')
            db.add_all([usuario,lead]);db.flush()
            lead.ejecutivo_id=usuario.id
            db.commit()
            uid,lid=usuario.id,lead.id
            permiso=ejecutar_consulta(db,usuario,Consulta(herramienta='cartera_resumen',alcance='general'))
            assert permiso['permitida'] is False and 'total' not in permiso
            resultado['casos']['ejecutivo_sin_resumen_general']='aprobado'

        def propuesta(titulo):
            with Session(motor) as db:
                p=models.PropuestaTareaChat(usuario_id=uid,solicitud='Solicitud ficticia de prueba',
                    salida_original='Propuesta simulada, sin llamada a IA',estado='pendiente',
                    propuesta={'accion':'crear_tarea','cliente':'Cliente temporal','titulo':titulo,'descripcion':None,'aclaracion':None})
                db.add(p);db.commit();return p.id

        def confirmar_en_paralelo(ids,titulo):
            barrera=Barrier(2); estado=local()
            def sincronizar(conn,cursor,statement,parameters,context,executemany):
                if 'FOR UPDATE' in statement.upper() and not getattr(estado,'sincronizado',False):
                    # Ambas transacciones alcanzan su bloqueo antes de continuar.
                    assert context.execution_options['schema_translate_map'][None]==esquema
                    estado.sincronizado=True;barrera.wait(timeout=15)
            event.listen(motor,'before_cursor_execute',sincronizar)
            def ejecutar(pid):
                with Session(motor) as db:
                    db.execute(text("SET LOCAL statement_timeout = '20s'"))
                    backend=db.execute(text('SELECT pg_backend_pid()')).scalar_one()
                    usuario=db.get(models.Usuario,uid)
                    try:
                        tarea=tareas_chat.confirmar(pid,tareas_chat.Confirmacion(lead_id=lid,titulo=titulo),db,usuario)
                        return {'estado':200,'tarea':tarea.id,'backend':backend}
                    except HTTPException as error:
                        db.rollback();return {'estado':error.status_code,'backend':backend}
            try:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    resultados=list(pool.map(ejecutar,ids))
                assert len({r['backend'] for r in resultados})==2, 'Se requieren dos conexiones simultáneas.'
                return resultados
            finally:
                event.remove(motor,'before_cursor_execute',sincronizar)

        pid=propuesta('Revisar requisitos')
        with Session(motor) as db:
            assert db.query(models.Tarea).count()==0
        resultado['casos']['propuesta_sin_guardado_automatico']='aprobado'
        resultados=confirmar_en_paralelo([pid,pid],'Revisar requisitos')
        assert [r['estado'] for r in resultados]==[200,200]
        assert len({r['tarea'] for r in resultados})==1
        with Session(motor) as db:
            assert db.query(models.Tarea).count()==1
            assert db.query(models.Auditoria).filter_by(entidad='tarea',accion='crear').count()==1
        resultado['casos']['misma_propuesta_dos_confirmaciones_una_tarea']='aprobado'

        ids=[propuesta('Confirmar visita'),propuesta('Confirmar visita')]
        resultados=confirmar_en_paralelo(ids,'Confirmar visita')
        assert sorted(r['estado'] for r in resultados)==[200,409]
        with Session(motor) as db:
            assert db.query(models.Tarea).filter_by(titulo='Confirmar visita').count()==1
            assert db.query(models.Tarea).count()==2
            assert db.get(models.Lead,lid).estado=='Nuevo'
        resultado['casos']['propuestas_distintas_mismo_seguimiento_sin_duplicar']='aprobado'
    finally:
        if creado:
            # Sólo el esquema que esta ejecución creó; nunca public ni un nombre externo.
            assert re.fullmatch(r'qa_mobilita_[0-9a-f]{32}',esquema)
            models.Base.metadata.drop_all(motor,tables=tablas)
            with database.engine.begin() as conexion:
                conexion.execute(DropSchema(esquema))
                assert conexion.execute(text('SELECT count(*) FROM pg_namespace WHERE nspname=:nombre'),{'nombre':esquema}).scalar_one()==0
            resultado['esquema_temporal_eliminado']=True
    return resultado


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ejecutar',action='store_true')
    if not parser.parse_args().ejecutar:
        parser.exit(message='Sin cambios. Usa --ejecutar para comprobar un esquema temporal en PostgreSQL.\n')
    resultado=verificar()
    ruta=Path(__file__).parent/'evidencias'/('mobilita_postgres_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')+'.json')
    ruta.parent.mkdir(exist_ok=True)
    ruta.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(resultado,ensure_ascii=True))
    print('Evidencia:',ruta.name)
