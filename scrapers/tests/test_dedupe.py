import pytest
from app.utils.dedupe import resolve_cross_source_duplicates
from app.models import Evento

def test_cross_source_dedupe_logic():
    # Mock some occurrences
    ev1 = Evento(nombre="Concierto de Melendi", fecha_iso="2026-05-20", lugar="Gran Canaria Arena", organiza="Tomaticket", url_venta="url1")
    ev2 = Evento(nombre="MELENDI EN CONCIERTO", fecha_iso="2026-05-20", lugar="GC Arena", organiza="Entrees", url_venta="url2")
    ev3 = Evento(nombre="Teatro", fecha_iso="2026-05-21", lugar="Teatro Cuyas", organiza="Tomaticket", url_venta="url3")
    
    from app.utils.dedupe import generate_occurrence_key
    print(f"Key1: {generate_occurrence_key(ev1.nombre, ev1.fecha_iso, ev1.lugar)}")
    print(f"Key2: {generate_occurrence_key(ev2.nombre, ev2.fecha_iso, ev2.lugar)}")
    
    eventos = [ev1, ev2, ev3]
    resolve_cross_source_duplicates(eventos)
    
    # ev1 and ev2 should have same group_id
    assert ev1.event_group_id == ev2.event_group_id
    # ev3 should have different group_id
    assert ev1.event_group_id != ev3.event_group_id
    assert ev1.event_group_id is not None
    assert ev3.event_group_id is not None
