import pytest
import datetime
from app.utils.parsers import _parsear_precio, _parsear_fecha, _parsear_hora, _validar_imagen
from app.utils.text_processing import normalizar_titulo_export, limpiar_lugar

def test_parsear_precio_basic():
    assert _parsear_precio("20€") == 20.0
    assert _parsear_precio("15.50 EUR") == 15.5
    assert _parsear_precio("Gratis") == 0.0
    assert _parsear_precio("Entrada Libre") == 0.0
    assert _parsear_precio("Precio: 🍒") is None
    assert _parsear_precio(None) is None
    assert _parsear_precio("") is None

def test_parsear_precio_desde():
    assert _parsear_precio("COMPRAR ENTRADAS - DESDE: 30 €") == 30.0
    assert _parsear_precio("A partir de 15,50") == 15.5

def test_parsear_precio_rango():
    assert _parsear_precio("10 - 20€") == 10.0
    assert _parsear_precio("15,50€ - 30.00€") == 15.5

def test_parsear_precio_absurde():
    assert _parsear_precio("1500€") is None
    assert _parsear_precio("501") is None
    assert _parsear_precio("500") is None

def test_parsear_fecha_iso():
    assert _parsear_fecha("2026-02-14T20:00:00") == "2026-02-14"
    assert _parsear_fecha("2026-06-25") == "2026-06-25"

def test_parsear_fecha_text():
    assert _parsear_fecha("Apertura de puertas 19:00 03/04/2026") == "2026-04-03"
    assert _parsear_fecha("14 de febrero 2026") == "2026-02-14"
    assert _parsear_fecha("14 de febrero") == "2026-02-14"
    assert _parsear_fecha("Varias Fechas (06/02/2026 - 30/04/2026)") == "2026-02-06"
    assert _parsear_fecha("Texto random sin fecha") is None
    assert _parsear_fecha("") is None

def test_parsear_hora_basic():
    assert _parsear_hora("20:30") == "20:30"
    assert _parsear_hora("Apertura de puertas 19:00 03/04/2026") == "19:00"
    assert _parsear_hora("a las 19:30") == "19:30"
    assert _parsear_hora("2026-02-14T20:00:00") == "20:00"
    assert _parsear_hora("19:30h") == "19:30"
    assert _parsear_hora("20.00") == "20:00"

def test_parsear_hora_improbable():
    # 10.31€ NO debe producir hora 10:31
    # Actually wait, my test needs to reflect actual behavior or I fix the behavior.
    assert _parsear_hora("10.31€") is None
    assert _parsear_hora("22:33") is None
    assert _parsear_hora("00:00") is None
    assert _parsear_hora("T12:00:00") is None
    assert _parsear_hora("12:04") is None

def test_validar_imagen():
    assert _validar_imagen("https://example.com/img.jpg") == "https://example.com/img.jpg"
    assert _validar_imagen("http://example.com/img.jpg") == "http://example.com/img.jpg"
    assert _validar_imagen("placeholder.png") is None
    assert _validar_imagen("noimage") is None
    assert _validar_imagen("NULL") is None
    assert _validar_imagen("https://short.com") is None  # < 20 chars
    assert _validar_imagen("/relative/path.jpg") is None

def test_normalizar_titulo_export():
    assert normalizar_titulo_export("Concierto en Gran Canaria") == "Concierto"
    assert normalizar_titulo_export("Concierto | Las Palmas de Gran Canaria") == "Concierto"
    assert normalizar_titulo_export("Concierto - Telde") == "Concierto"
    assert normalizar_titulo_export("Concierto Islas Canarias") == "Concierto"
    assert normalizar_titulo_export(None) == ""

def test_limpiar_lugar():
    assert limpiar_lugar("Teatro Pérez Galdos") == "Teatro Pérez Galdós"
    assert limpiar_lugar("Auditorio A. Kraus") == "Auditorio Alfredo Kraus"
    assert limpiar_lugar("GC Arena") == "Gran Canaria Arena"
    assert limpiar_lugar("vive la experiencia en el parque") is None
    assert limpiar_lugar("https://example.com") is None
    assert limpiar_lugar("conoce al autor") is None
    assert limpiar_lugar(None) is None
    assert limpiar_lugar("") is None
    assert limpiar_lugar("x" * 151) is None
    assert limpiar_lugar("  Estadio de Gran Canaria  ") == "Estadio de Gran Canaria"
    assert limpiar_lugar("Paseo nocturno guiado") is None
    assert limpiar_lugar("Infecar, pabellon 7") == "INFECAR"
    assert limpiar_lugar("Teatro Cuyas Las Palmas") == "Teatro Cuyás"
    assert limpiar_lugar("Fundacion Cicca") == "Fundación CICCA"
    assert limpiar_lugar("Descubre los secretos mágicos") is None
    
def test_parsear_precio_edge_cases():
    assert _parsear_precio("12,50 euros") == 12.5
    assert _parsear_precio("eur 10") == 10.0
    assert _parsear_precio("A partir de 15,50") == 15.5
    assert _parsear_precio("desde:30€") == 30.0
    assert _parsear_precio("50 - 60 eur") == 50.0
    assert _parsear_precio("Entrada libre y gratuita") == 0.0
    assert _parsear_precio("1000€") is None
    assert _parsear_precio("precio: 10,00€") == 10.0
    assert _parsear_precio("eur 499.99") == 499.99
    
def test_parsear_fecha_edge_cases():
    assert _parsear_fecha("1/2/2026") == "2026-02-01"
    assert _parsear_fecha("01-02-26") == "2026-02-01"
    assert _parsear_fecha("15 del mes de febrero") is None
    assert _parsear_fecha("15 de enero del 2026") == "2026-01-15"
    assert _parsear_fecha("31 DE DICIEMBRE") == "2026-12-31"
    assert _parsear_fecha("2026-12-31T23:59:59") == "2026-12-31"

def test_parsear_hora_edge_cases():
    assert _parsear_hora("A las 8:30") == "08:30"
    assert _parsear_hora("a las 23.59") == "23:59"
    assert _parsear_hora("19hrs") == "19:00"
    assert _parsear_hora("20 h") == "20:00"
    assert _parsear_hora("2026-02-14T20:00:00") == "20:00"
    assert _parsear_hora("T12:00:00") is None
    assert _parsear_hora("08:00") is None  # Improbable culture event start
    assert _parsear_hora("25:00") is None
    assert _parsear_hora("19:60") is None
    # Bulk cases from logs
    cases = [
        ("Inicia 18:30h", "18:30"),
        ("20:45 aprox.", "20:45"),
        ("Apertura 19:00", "19:00"),
        ("12:00:00", None), # Improbable
        ("22:33", None),    # Sentinel
        ("00:00", None),    # Sentinel/Default
        ("9 h.", "09:00"),
        ("10.30€", None),   # Price, not hour
    ]
    for txt, expected in cases:
        assert _parsear_hora(txt) == expected

def test_parsear_precio_bulk():
    cases = [
        ("Entradas desde 15€", 15.0),
        ("Gratis", 0.0),
        ("A partir de 12.50", 12.5),
        ("30 € / 45 €", 30.0),
        ("Precio: 10,99 EUR", 10.99),
        ("Descuento 50% (Precio final 20€)", 20.0),
        ("Comprar entradas - Desde: 30 €", 30.0),
        ("Taquilla 25,00€", 25.0),
        ("Gastos de gestión 2.50€", 2.5),
        ("10.31€", 10.31),
    ]
    for txt, expected in cases:
        assert _parsear_precio(txt) == expected

def test_parsear_fecha_bulk():
    cases = [
        ("Del 1 al 10 de Mayo 2026", "2026-05-01"),
        ("01/01/26", "2026-01-01"),
        ("2026-02-14", "2026-02-14"), # Simple ISO
        ("Varias Fechas (06/02/2026 - 30/04/2026)", "2026-02-06"),
    ]
    for txt, expected in cases:
        assert _parsear_fecha(txt) == expected

def test_limpiar_texto():
    from app.utils.text_processing import limpiar_texto
    assert limpiar_texto("  hola   mundo  ") == "hola mundo"
    assert limpiar_texto("hola\u200bmundo") == "holamundo"
    assert limpiar_texto(None) == ""

def test_inferir_nombre():
    from app.utils.text_processing import inferir_nombre
    assert inferir_nombre("https://entradas.com/evento/lago-cisnes") == "Lago Cisnes"
    assert inferir_nombre("/evento/123456-concierto-fantastico/") == "Concierto Fantastico"
    assert inferir_nombre(None) == "Evento Cultural"
    assert inferir_nombre("") == "Evento Cultural"

def test_normalizar_fecha_text():
    from app.utils.text_processing import normalizar_fecha
    assert normalizar_fecha("15 de Marzo") == "2026-03-15"
    assert normalizar_fecha("1 de Ene") == "2026-01-01"
    assert normalizar_fecha("No hay fecha") is None

def test_categorizar_pro():
    from app.utils.text_processing import categorizar_pro
    # categorizar_pro ahora siempre devuelve "Otros" — la clasificación
    # real la hace el classifier.py con IA sobre título + descripción.
    assert categorizar_pro("Concierto de Rock", "Tomaticket") == "Otros"
    assert categorizar_pro("Caperucita Roja", "Teatro Pérez Galdós") == "Otros"
    assert categorizar_pro("Carnaval de Las Palmas", "Fuente X") == "Otros"
    assert categorizar_pro("Charla sobre IA", "Fuente Y") == "Otros"

def test_validar_imagen():
    from app.scrapers._enrichment import _validar_imagen
    assert _validar_imagen("https://img.com/a.jpg") == "https://img.com/a.jpg"
    assert _validar_imagen("data:image/png;base64,...") is None
    assert _validar_imagen("http://sh.ort") is None
    assert _validar_imagen("transparent.gif") is None
    assert _validar_imagen("") is None

def test_es_titulo_generico():
    from app.utils.parsers import es_titulo_generico
    assert es_titulo_generico("Entradas para el concierto") == True
    assert es_titulo_generico("Melendi en concierto") == False
    assert es_titulo_generico("Tickety") == True
    assert es_titulo_generico("") == True

def test_es_paja():
    from app.utils.parsers import es_paja
    assert es_paja("Política de privacidad y aviso legal") == True
    assert es_paja("Este es un gran concierto de rock") == False
    assert es_paja(None) == False

