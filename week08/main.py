import tkinter as tk
from tkinter import ttk, messagebox

# =================================================================
# 1. 비즈니스 로직 (Business Logic: 계산 엔진)
# =================================================================
class ParkingCalculator:
    """주차 요금을 계산하는 순수 로직 클래스"""
    
    @staticmethod
    def time_to_minutes(time_str):
        """'HH:mm' 형식을 총 분(minutes)으로 변환"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def calculate_fee(start_min, end_min):
        """요금 계산: 30분 무료, 10분당 500원(야간 600원), 최대 20,000원"""
        if start_min is None or end_min is None or end_min <= start_min:
            return 0
            
        total_duration = end_min - start_min
        
        # 30분까지 무료 처리
        if total_duration <= 30:
            return 0

        fee = 0
        # 유료 시작점: 입차 후 30분이 지난 시점부터
        current_pointer = start_min + 30
        
        while current_pointer < end_min:
            # 10분 단위로 끊어서 계산 (남은 시간이 10분 미만이어도 1회로 계산)
            next_pointer = min(current_pointer + 10, end_min)
            
            # 해당 10분 블록의 중앙값이 야간(00:00~06:00) 구간인지 판별
            mid_time = (current_pointer + next_pointer - 1) / 2
            is_night = 0 <= mid_time < 360
            
            # 야간은 600원, 일반은 500원
            unit_price = 600 if is_night else 500
            fee += unit_price
            
            current_pointer = next_pointer

        # 일일 최대 요금 20,000원 제한 적용
        return min(fee, 20000)


# =================================================================
# 2. 프레젠테이션 레이어 (Presentation Layer: GUI 화면)
# =================================================================
class ParkingGUI:
    """사용자 인터페이스(GUI)를 관리하는 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 주차 요금 관리 시스템")
        self.root.geometry("650x500")
        self.calc = ParkingCalculator()
        self.records = []

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        """UI 디자인 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure("Treeview.Heading", font=('Malgun Gothic', 10, 'bold'))
        style.configure("TButton", font=('Malgun Gothic', 10))
        style.configure("Total.TLabel", font=('Malgun Gothic', 14, 'bold'))

    def _create_widgets(self):
        """화면의 모든 구성 요소 생성 및 배치"""
        # [입력 영역]
        input_frame = ttk.LabelFrame(self.root, text=" 주차 정보 입력 ", padding=15)
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="입차 (HH:mm):").grid(row=0, column=0, padx=5, pady=5)
        self.arrival_entry = ttk.Entry(input_frame, width=10)
        self.arrival_entry.insert(0, "09:00")
        self.arrival_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="출차 (HH:mm):").grid(row=0, column=2, padx=5, pady=5)
        self.departure_entry = ttk.Entry(input_frame, width=10)
        self.departure_entry.insert(0, "10:00")
        self.departure_entry.grid(row=0, column=3, padx=5, pady=5)

        self.add_btn = ttk.Button(input_frame, text="기록 추가", command=self.add_record)
        self.add_btn.grid(row=0, column=4, padx=10, pady=5)

        # [목록 테이블 영역]
        list_frame = ttk.Frame(self.root, padding=10)
        list_frame.pack(fill="both", expand=True, padx=20)

        columns = ("arrival", "departure", "duration", "fee")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree.heading("arrival", text="입차")
        self.tree.heading("departure", text="출차")
        self.tree.heading("duration", text="주차시간")
        self.tree.heading("fee", text="요금")

        self.tree.column("arrival", width=80, anchor="center")
        self.tree.column("departure", width=80, anchor="center")
        self.tree.column("duration", width=100, anchor="center")
        self.tree.column("fee", width=100, anchor="e")

        self.tree.pack(side="left", fill="both", expand=True)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # [하단 컨트롤 및 합계 영역]
        bottom_frame = ttk.Frame(self.root, padding=15)
        bottom_frame.pack(fill="x", padx=20, pady=10)

        self.delete_btn = ttk.Button(bottom_frame, text="선택 삭제", command=self.delete_selected)
        self.delete_btn.pack(side="left")

        self.total_label = ttk.Label(bottom_frame, text="총 합계: 0원", style="Total.TLabel")
        self.total_label.pack(side="right")

    # --- 이벤트 핸들러 (Logic Integration) ---

    def add_record(self):
        """입력 데이터를 읽어 요금을 계산하고 테이블에 추가"""
        arrival = self.arrival_entry.get()
        departure = self.departure_entry.get()

        start_min = self.calc.time_to_minutes(arrival)
        end_min = self.calc.time_to_minutes(departure)

        if start_min is None or end_min is None:
            messagebox.showerror("입력 오류", "시간 형식이 잘못되었습니다. (예: 09:30)")
            return

        if end_min <= start_min:
            messagebox.showerror("시간 오류", "출차 시간은 입차 시간보다 뒤여야 합니다.")
            return

        # 주차 시간 포맷팅 (H시간 M분)
        duration_total = end_min - start_min
        hours, minutes = divmod(duration_total, 60)
        
        # 요금 계산 (핵심 로직 호출)
        fee = self.calc.calculate_fee(start_min, end_min)

        # 기록 저장
        self.records.append({
            "arrival": arrival,
            "departure": departure,
            "duration": f"{hours}시간 {minutes}분",
            "fee": fee
        })
        self.refresh_table()

    def delete_selected(self):
        """선택된 행을 삭제하고 합계를 갱신"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("삭제 알림", "삭제할 항목을 목록에서 선택해주세요.")
            return

        for item in selected_items:
            index = self.tree.index(item)
            del self.records[index]
            self.tree.delete(item)

        self.refresh_total_only()

    def refresh_table(self):
        """전체 데이터 리스트를 바탕으로 표와 합계를 모두 새로고침"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_sum = 0
        for r in self.records:
            self.tree.insert("", "end", values=(
                r["arrival"], 
                r["departure"], 
                r["duration"], 
                f"{r['fee']:,}원"
            ))
            total_sum += r["fee"]

        self.total_label.config(text=f"총 합계: {total_sum:,}원")

    def refresh_total_only(self):
        """삭제 시 효율성을 위해 합계만 다시 계산"""
        total_sum = sum(r["fee"] for r in self.records)
        self.total_label.config(text=f"총 합계: {total_sum:,}원")


# =================================================================
# 3. 프로그램 진입점 (Main Entry Point)
# =================================================================
if __name__ == "__main__":
    # Tkinter 엔진 초기화
    root = tk.Tk()
    
    # 애플리케이션 실행
    app = ParkingGUI(root)
    
    # 메인 루프 실행 (창이 닫힐 때까지 프로그램 유지)
    root.mainloop()
