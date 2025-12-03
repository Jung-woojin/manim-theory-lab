from manim import *
import numpy as np

class ERFPanelCompare_Final(Scene):
    def construct(self):
        K1, K2 = 3, 17
        sigma1 = K1 / 3.0
        sigma2 = K2 / 3.0

        N = 20
        c = N // 2

        cell = 0.22
        gap = 0.010
        IMG_SCALE = 0.65
        HM_CELL = 0.085

        TITLE_FS = 22
        LABEL_FS = 22

        def make_image_grid(N, cell, gap):
            squares = VGroup()
            for _ in range(N * N):
                sq = Square(side_length=cell)
                sq.set_fill(BLACK, opacity=1.0)
                sq.set_stroke(color=GRAY_C, width=0.55)
                squares.add(sq)
            squares.arrange_in_grid(rows=N, cols=N, buff=gap)
            return squares

        img = make_image_grid(N, cell, gap).scale(IMG_SCALE)
        img_title = Text(f"Input Image ({N}×{N})", font_size=TITLE_FS).next_to(
            img, UP, buff=0.38
        )
        img_group = VGroup(img_title, img)
        img_group.move_to(LEFT*3.15 + UP*0.05)
        self.play(FadeIn(img_group))

        # --- ERF 히트맵 준비 ---
        xs = np.arange(N) - c
        ys = np.arange(N) - c
        X, Y = np.meshgrid(xs, ys)

        def erf_gaussian(sigma):
            G = np.exp(-(X**2 + Y**2) / (2 * sigma**2))
            G /= G.sum()
            return G

        def heatmap(A, cell_size, title):
            vmin, vmax = A.min(), A.max()

            def val_to_color(v):
                t = (v - vmin) / (vmax - vmin + 1e-9)
                return interpolate_color(BLACK, WHITE, t)

            squares = VGroup()
            for i in range(A.shape[0]):
                for j in range(A.shape[1]):
                    sq = Square(side_length=cell_size)
                    sq.set_fill(val_to_color(A[i, j]), opacity=1.0)
                    sq.set_stroke(color=GRAY_D, width=0.3)
                    squares.add(sq)

            squares.arrange_in_grid(rows=A.shape[0], cols=A.shape[1], buff=0.005)
            title_m = Text(title, font_size=18)

            group = VGroup(title_m, squares).arrange(DOWN, buff=0.08)
            box = SurroundingRectangle(squares, color=WHITE, buff=0.025)
            group.add(box)
            return group

        ERF1 = erf_gaussian(sigma1)
        ERF2 = erf_gaussian(sigma2)

        hm1 = heatmap(ERF1, HM_CELL, "ERF after 3×3 filter")
        hm2 = heatmap(ERF2, HM_CELL, "ERF after 17×17 filter")

        # ✅ 오른쪽 패널 "자리"만 먼저 만들어 두기 (플레이스홀더)
        placeholder1 = Rectangle(width=2.4, height=2.4, stroke_color=GRAY_E, stroke_width=1.5)
        placeholder2 = Rectangle(width=2.4, height=2.4, stroke_color=GRAY_E, stroke_width=1.5)
        erf_panel = VGroup(placeholder1, placeholder2).arrange(DOWN, buff=0.5)
        erf_panel.move_to(RIGHT*3.35 + DOWN*0.1)

        self.add(erf_panel)

        # --- 스캔 함수 ---
        def pad_and_slide_scan(K, color, label_text):
            pad = K // 2
            unit = (cell + gap) * IMG_SCALE

            pad_rect = SurroundingRectangle(
                img,
                buff=pad * unit,
                color=color,
                stroke_width=2.6
            )

            k_label = Text(label_text, font_size=LABEL_FS, color=color)
            pad_label = Text(f"Padding = {pad}", font_size=LABEL_FS, color=color)
            info_panel = VGroup(k_label, pad_label).arrange(DOWN, buff=0.10)

            if K == 3:
                info_panel.next_to(pad_rect, DOWN, buff=0.28)
            else:
                info_panel.next_to(img, DOWN, buff=0.18)

            win_size = (K * cell + (K - 1) * gap) * IMG_SCALE
            window = Square(side_length=win_size, color=color, stroke_width=2.6)
            window.set_fill(color, opacity=0.08)

            self.play(Create(pad_rect), FadeIn(info_panel), FadeIn(window))

            N_pad = N + 2 * pad

            left_x  = pad_rect.get_left()[0]   + win_size / 2
            right_x = pad_rect.get_right()[0]  - win_size / 2
            top_y   = pad_rect.get_top()[1]    - win_size / 2
            bot_y   = pad_rect.get_bottom()[1] + win_size / 2

            cols = N_pad - 2 * pad
            rows = N_pad - 2 * pad

            x_positions = np.linspace(left_x, right_x, cols)
            y_positions = np.linspace(top_y, bot_y, rows)

            scan_points = []
            for yi, y in enumerate(y_positions):
                for x in x_positions:
                    scan_points.append(np.array([x, y, 0]))
                if yi < len(y_positions) - 1:
                    scan_points.append(np.array([x_positions[0], y_positions[yi+1], 0]))

            path = VMobject().set_points_as_corners(scan_points)
            window.move_to(scan_points[0])

            self.play(MoveAlongPath(window, path, rate_func=linear), run_time=10.0)
            self.play(FadeOut(window), FadeOut(pad_rect), FadeOut(info_panel))

        # ----------------------------
        # 3×3 스캔 → 오른쪽 위 ERF 표시
        # ----------------------------
        pad_and_slide_scan(K1, BLUE, "3×3 Filter scan")

        hm1.move_to(placeholder1.get_center())
        self.play(FadeIn(hm1), run_time=0.6)
        self.wait(0.4)

        # ----------------------------
        # 17×17 스캔 → 오른쪽 아래 ERF 표시
        # ----------------------------
        pad_and_slide_scan(K2, RED, "17×17 Filter scan")

        hm2.move_to(placeholder2.get_center())
        self.play(FadeIn(hm2), run_time=0.3)
        self.wait(0.6)

        end_txt = Text("Large kernel → wider ERF", font_size=20)
        end_txt.next_to(erf_panel, UP, buff=0.18)
        self.play(FadeIn(end_txt))
        self.wait(1.2)
