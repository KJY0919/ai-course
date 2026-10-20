from calculator import ParkingCalculator

def run_tests():
    calc = ParkingCalculator()
    test_cases = [
        {"name": "TC-01: 30분 이내 무료", "start": "09:00", "end": "09:20", "expected": 0},
        {"name": "TC-02: 40분 주차 (10분 과금)", "start": "09:00", "end": "09:40", "expected": 500},
        {"name": "TC-03: 60분 주차 (30분 과금)", "start": "09:00", "end": "10:00", "expected": 1500},
        {"name": "TC-04: 야간 주차 (60분)", "start": "00:00", "end": "01:00", "expected": 3000},
        {"name": "TC-05: 최대 요금 제한", "start": "09:00", "end": "20:00", "expected": 20000},
    ]

    passed = 0
    failed = 0

    print("🚀 테스트를 시작합니다...\n")

    for tc in test_cases:
        s = calc.time_to_minutes(tc["start"])
        e = calc.time_to_minutes(tc["end"])
        actual = calc.calculate_fee(s, e)

        if actual == tc["expected"]:
            print(f"✅ [PASS] {tc['name']}")
            passed += 1
        else:
            print(f"❌ [FAIL] {tc['name']} | 기대값: {tc['expected']}, 결과값: {actual}")
            failed += 1

    print("\n" + "="*30)
    print(f"결과 요약: 통과 {passed}, 실패 {failed}")
    print("="*30)

    if failed > 0:
        exit(1)

if __name__ == "__main__":
    run_tests()
