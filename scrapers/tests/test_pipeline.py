import pytest
from unittest.mock import MagicMock, AsyncMock
from app.scrapers._enrichment import extraer_datos_duros
from app.utils.parsers import _parsear_precio, _parsear_fecha, _parsear_hora

@pytest.mark.asyncio
async def test_extraer_datos_duros_mocked():
    # Mock Playwright Page
    page = AsyncMock()
    
    # Mock body inner_text for Layer 3 (Regex)
    # We include a date and a price in the simulated HTML text
    page.inner_text.return_value = "Gran concierto el 15/05/2026 a las 21:00. Entradas desde 25€."
    
    # Mock _extraer_json_ld to return nothing (force Layer 2/3)
    # We patch the internal call or just rely on the fallback logic
    
    url = "https://example.com/evento/concierto-test"
    
    # We need to mock _extraer_json_ld which is in the same module
    with MagicMock() as mock_ld:
        # Since extraer_datos_duros calls _extraer_json_ld(page)
        # and _extraer_json_ld is defined in app.scrapers._enrichment
        pass

    result = await extraer_datos_duros(page, url)
    
    # Verify Layer 3 works
    assert result["precio_num"] == 25.0
    assert result["fecha_iso"] == "2026-05-15"
    assert result["hora"] == "21:00"

@pytest.mark.asyncio
async def test_extraer_datos_duros_galdos_mock():
    # Simulate Teatro Pérez Galdós DOM structure
    page = AsyncMock()
    
    # Layer 3 fallback text
    page.inner_text.side_effect = lambda sel, **kwargs: {
        "body": "Teatro Pérez Galdós. Fecha: 20 de marzo de 2026. Horario: 20:30 h. Precio: 15€",
        ".info p": "20 de marzo de 2026",
    }.get(sel, "")

    # Mock locator for CSS selectors (Layer 2)
    mock_locator = MagicMock()
    mock_locator.count.return_value = 1
    mock_locator.first = mock_locator
    mock_locator.inner_text.return_value = "20 de marzo de 2026"
    page.locator.return_value = mock_locator

    url = "https://teatroperezgaldos.es/evento/test/123"
    result = await extraer_datos_duros(page, url)
    
    assert result["fecha_iso"] == "2026-03-20"
    # Note: For Galdos, if _parsear_hora isn't in the date string, 
    # it should be picked up by Layer 3 body search
    assert result["hora"] == "20:30"
