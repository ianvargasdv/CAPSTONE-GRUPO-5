"""Orígenes de publicación: base temporal, sin red ni proveedor de IA."""
import os
import unittest

os.environ['CORS_ORIGINS'] = 'https://crm-publicacion.example.test'
from prueba_catalogo import ClientePruebas
from origenes import cargar_origenes


class PublicacionTest(unittest.TestCase):
    def test_conserva_el_desarrollo_local(self):
        self.assertEqual(cargar_origenes(), ['http://localhost:3000', 'http://127.0.0.1:3000'])

    def test_normaliza_y_no_duplica_origenes(self):
        resultado = cargar_origenes(' https://CRM.example.test:443/,https://crm.example.test,http://localhost:3000 ')
        self.assertEqual(resultado, ['http://localhost:3000', 'http://127.0.0.1:3000', 'https://crm.example.test'])

    def test_admite_mas_de_un_dominio_concreto(self):
        resultado = cargar_origenes('https://uno.example.test,https://dos.example.test:8443')
        self.assertIn('https://uno.example.test', resultado)
        self.assertIn('https://dos.example.test:8443', resultado)

    def test_rechaza_comodines_rutas_credenciales_y_urls_invalidas(self):
        for valor in ['*', 'https://*.pages.dev', 'https://example.test/api',
                      'https://cuenta:clave-ficticia@example.test', 'https://example.test?token=ficticio',
                      'https://example.test#fragmento', 'ftp://example.test', 'https://',
                      'https://example.test:puerto', 'https://exa mple.test']:
            with self.subTest(valor=valor), self.assertRaises(ValueError) as error:
                cargar_origenes(valor)
            self.assertNotIn('clave-ficticia', str(error.exception))
            self.assertNotIn('token=ficticio', str(error.exception))

    def preflight(self, origen):
        return ClientePruebas().solicitar('OPTIONS', '/api/leads', cabeceras=[
            (b'origin', origen.encode()), (b'access-control-request-method', b'GET'),
            (b'access-control-request-headers', b'authorization,content-type'),
        ])

    def test_acepta_la_interfaz_publicada(self):
        self.assertEqual(self.preflight('https://crm-publicacion.example.test').status_code, 200)

    def test_rechaza_otro_sitio_y_un_nombre_parecido(self):
        for origen in ['https://otro.example.test', 'https://crm-publicacion.example.test.otro.test']:
            self.assertEqual(self.preflight(origen).status_code, 400)

    def test_conserva_el_origen_local(self):
        self.assertEqual(self.preflight('http://localhost:3000').status_code, 200)

    def test_un_origen_permitido_no_sustituye_la_autenticacion(self):
        respuesta = ClientePruebas().solicitar('GET', '/api/leads', cabeceras=[
            (b'origin', b'https://crm-publicacion.example.test'),
        ])
        self.assertEqual(respuesta.status_code, 401)


if __name__ == '__main__':
    unittest.main()
