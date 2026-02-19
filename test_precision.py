"""
Tests for the precision scraping extraction functions (v4).
Validates _parsear_precio, _parsear_fecha, _parsear_hora, _validar_imagen, _detectar_dominio.
"""

import pytest
from app.scrapers._enrichment import (
    _parsear_precio,
    _parsear_fecha,
    _parsear_hora,
    _validar_imagen,
    _detectar_dominio,
)


class TestParsearPrecio:
    def test_precio_basico(self):
        assert _parsear_precio("30 €") == 30.0

    def test_precio_decimal_coma(self):
        assert _parsear_precio("15,50€") == 15.5

    def test_precio_decimal_punto(self):
        assert _parsear_precio("15.50€") == 15.5

    def test_precio_desde(self):
        assert _parsear_precio("Desde 25€") == 25.0

    def test_precio_desde_con_espacios(self):
        assert _parsear_precio("COMPRAR ENTRADAS - DESDE: 30 €") == 30.0

    def test_precio_rango(self):
        assert _parsear_precio("15-30€") == 15.0

    def test_precio_rango_con_guion_largo(self):
        assert _parsear_precio("10,80 € – 19,07 €") == 10.8

    def test_precio_gratis(self):
        assert _parsear_precio("Entrada libre") == 0.0
        assert _parsear_precio("Gratis") == 0.0
        assert _parsear_precio("Gratuito") == 0.0

    def test_precio_euros_text(self):
        assert _parsear_precio("50 euros") == 50.0

    def test_precio_none(self):
        assert _parsear_precio("") is None
        assert _parsear_precio(None) is None

    def test_precio_sin_numero(self):
        assert _parsear_precio("Próximamente") is None

    def test_precio_boton_tomaticket(self):
        """Simula el texto real del #BotonExterno de Tomaticket."""
        assert _parsear_precio("COMPRAR ENTRADAS - DESDE: 30 €") == 30.0

    def test_precio_janto(self):
        """Simula precios de la tabla de Janto."""
        assert _parsear_precio("27,00€") == 27.0


class TestParsearFecha:
    def test_fecha_iso(self):
        assert _parsear_fecha("2026-02-14") == "2026-02-14"

    def test_fecha_iso_con_hora(self):
        assert _parsear_fecha("2026-02-14T20:00:00") == "2026-02-14"

    def test_fecha_dmy_slash(self):
        assert _parsear_fecha("10/03/2026") == "2026-03-10"

    def test_fecha_dmy_slash_con_hora(self):
        assert _parsear_fecha("10/03/2026 a las 19:30") == "2026-03-10"

    def test_fecha_texto(self):
        assert _parsear_fecha("26 de febrero de 2026") == "2026-02-26"

    def test_fecha_texto_sin_anio(self):
        assert _parsear_fecha("14 de febrero") == "2026-02-14"

    def test_fecha_none(self):
        assert _parsear_fecha("") is None
        assert _parsear_fecha(None) is None


class TestParsearHora:
    def test_hora_a_las(self):
        assert _parsear_hora("a las 19:30") == "19:30"

    def test_hora_a_las_con_fecha(self):
        assert _parsear_hora("10/03/2026 a las 19:30") == "19:30"

    def test_hora_formato_h(self):
        assert _parsear_hora("20:00 h") == "20:00"

    def test_hora_iso(self):
        assert _parsear_hora("2026-02-14T20:00:00") == "20:00"

    def test_hora_sola(self):
        assert _parsear_hora(" 19:30") == "19:30"

    def test_hora_none(self):
        assert _parsear_hora("") is None
        assert _parsear_hora(None) is None


class TestValidarImagen:
    def test_imagen_valida(self):
        assert _validar_imagen("https://example.com/image.jpg") == "https://example.com/image.jpg"

    def test_imagen_null(self):
        assert _validar_imagen("https://images.tomaticket.com/eventos/eNULL") is None

    def test_imagen_null_mayusculas(self):
        assert _validar_imagen("https://static.tomaticket.com/images/static/NULL.jpeg") is None

    def test_imagen_placeholder(self):
        assert _validar_imagen("https://example.com/placeholder.jpg") is None

    def test_imagen_none(self):
        assert _validar_imagen(None) is None
        assert _validar_imagen("") is None

    def test_imagen_no_http(self):
        assert _validar_imagen("//example.com/image.jpg") is None

    def test_imagen_corta(self):
        assert _validar_imagen("http://x.co") is None

    def test_imagen_default(self):
        assert _validar_imagen("https://example.com/DEFAULT-image.png") is None


class TestDetectarDominio:
    def test_tomaticket(self):
        assert _detectar_dominio("https://www.tomaticket.es/es-es/event") == "tomaticket"

    def test_auditorio(self):
        assert _detectar_dominio("https://auditorioalfredokraus.es/evento/test") == "auditorio"

    def test_teatro_galdos(self):
        assert _detectar_dominio("https://teatroperezgaldos.es/evento/test") == "teatro_galdos"

    def test_guiniguada(self):
        assert _detectar_dominio("https://www3.gobiernodecanarias.org/cultura/ocio/teatroguiniguada/") == "guiniguada"

    def test_cicca(self):
        assert _detectar_dominio("https://www.fundacionlacajadecanarias.es/evento/") == "cicca"

    def test_tickety(self):
        assert _detectar_dominio("https://tickety.es/event/test") == "tickety"

    def test_ticketmaster(self):
        assert _detectar_dominio("https://www.ticketmaster.es/event/test") == "ticketmaster"

    def test_janto(self):
        assert _detectar_dominio("https://ofgc.janto.es/janto/main.php") == "janto"

    def test_generico(self):
        assert _detectar_dominio("https://www.example.com/event") == "generico"
