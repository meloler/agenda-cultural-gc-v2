import pytest
from unittest.mock import AsyncMock, MagicMock
from app.scrapers.tomaticket import scrape_tomaticket
from app.scrapers.entradas_canarias import scrape_entradas_canarias
from app.scrapers.institucional import scrape_cicca, scrape_guiniguada
from app.scrapers.entrees import scrape_entrees
from app.scrapers.cultura_canaria import scrape_cultura_canaria
from app.scrapers.entradas_com import scrape_entradas_com
from app.scrapers.telde_cultura import scrape_telde_cultura

@pytest.fixture
def mock_page():
    page = AsyncMock()
    page.goto = AsyncMock(return_value=None)
    # Simple locator mock that returns a count of 0 to avoid crashing
    mock_loc = AsyncMock()
    mock_loc.count = AsyncMock(return_value=0)
    page.locator = MagicMock(return_value=mock_loc)
    page.query_selector_all = AsyncMock(return_value=[])
    return page

@pytest.mark.asyncio
async def test_tomaticket_harness(mock_page):
    eventos = await scrape_tomaticket(mock_page)
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_entradascanarias_harness(mock_page):
    eventos = await scrape_entradas_canarias(mock_page)
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_cicca_harness(mock_page):
    eventos = await scrape_cicca(mock_page)
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_guiniguada_harness(mock_page):
    eventos = await scrape_guiniguada(mock_page)
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_entrees_harness(mock_page):
    eventos = await scrape_entrees(mock_page)
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_cultura_canaria_harness(mock_page):
    # Test Auditorio / Perez Galdos generic function
    eventos = await scrape_cultura_canaria(mock_page, "https://example.com", "Lugar Test")
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_entradas_com_harness(mock_page):
    eventos = await scrape_entradas_com(mock_page)
    assert isinstance(eventos, list)

@pytest.mark.asyncio
async def test_telde_cultura_harness(mock_page):
    eventos = await scrape_telde_cultura(mock_page)
    assert isinstance(eventos, list)
