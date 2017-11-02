from textgrid import TextGrid
from decimal import Decimal


def test_read_short(short_format_file):
    tg = TextGrid()
    tg.read(short_format_file)
    assert tg.tiers[0].name == 'phone'
    assert tg.tiers[1].name == 'word'
    assert tg.tiers[0][0].mark == 'sil'
    assert abs(tg.tiers[0][0].minTime - Decimal(1358.8925)) < 0.01
    assert abs(tg.tiers[0][0].maxTime == Decimal(1361.8925)) < 0.01
