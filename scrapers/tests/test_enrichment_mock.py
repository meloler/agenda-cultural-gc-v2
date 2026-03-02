import pytest
from unittest.mock import AsyncMock, MagicMock
from app.scrapers._enrichment import enriquecer_evento

@pytest.mark.asyncio
async def test_enriquecer_evento_mock():
    mock_page = AsyncMock()
    # Mocking various DOM elements
    mock_el = AsyncMock()
    mock_el.inner_text = AsyncMock(return_value="Precio: 15€")
    mock_el.get_attribute = AsyncMock(return_value="https://img.com/a.jpg")
    
    mock_page.goto = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=mock_el)
    mock_page.query_selector_all = AsyncMock(return_value=[mock_el])
    mock_page.content = AsyncMock(return_value="<html><body>15/05/2026 20:30</body></html>")
    
    seen = set()
    res = await enriquecer_evento(mock_page, "http://test.com", "Concierto", seen)
    
    assert isinstance(res, dict)
    assert "precio_num" in res
    assert "fecha_iso" in res
    assert "descripcion" in res
