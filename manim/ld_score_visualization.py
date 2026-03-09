from manim import *


class LDScoreVisualization(Scene):
    def construct(self):
        pause_short = 0.5
        pause_long = 1.1

        highlight_color = GREEN
        eq_color = GREEN

        # ------------------------------------------------------------
        # Helpers
        # ------------------------------------------------------------
        def make_matrix():
            """
            A 5x5-looking correlation matrix without cell borders.
            Dots indicate that the full matrix continues up to M SNPs.
            """
            entries = [
                [r"\rho_{11}", r"\rho_{12}", r"\rho_{13}", r"\cdots", r"\rho_{1M}"],
                [r"\rho_{21}", r"\rho_{22}", r"\rho_{23}", r"\cdots", r"\rho_{2M}"],
                [r"\rho_{31}", r"\rho_{32}", r"\rho_{33}", r"\cdots", r"\rho_{3M}"],
                [r"\vdots",    r"\vdots",    r"\vdots",    r"\ddots", r"\vdots"],
                [r"\rho_{M1}", r"\rho_{M2}", r"\rho_{M3}", r"\cdots", r"\rho_{MM}"],
            ]

            matrix = Matrix(
                entries,
                element_to_mobject=lambda s: MathTex(s, font_size=32),
                h_buff=1.0,
                v_buff=0.7,
                bracket_h_buff=0.15,
                bracket_v_buff=0.15,
            )

            label = MathTex(r"\mathbf{R} =", font_size=42)
            label.next_to(matrix, LEFT, buff=0.18)

            full = VGroup(label, matrix)
            return full, matrix

        def get_entry(matrix, r, c):
            # Matrix entries are returned row-major as a flat VGroup
            return matrix.get_entries()[r * 5 + c]

        def get_column_entries(matrix, col_idx):
            # Skip the row of vertical dots (row index 3)
            return VGroup(*[get_entry(matrix, r, col_idx) for r in [0, 1, 2, 4]])

        # ------------------------------------------------------------
        # Introduce the general equation, then remove it
        # ------------------------------------------------------------
        general_eq = MathTex(
            r"\ell_j = \sum_{k=1}^{M} \rho_{kj}^2",
            font_size=54,
            color=eq_color
        )
        general_eq.to_edge(UP, buff=0.6)

        self.play(Write(general_eq))
        self.wait(pause_long)
        self.play(FadeOut(general_eq))
        self.wait(0.15)

        # ------------------------------------------------------------
        # Show the matrix
        # ------------------------------------------------------------
        matrix_group, matrix = make_matrix()
        matrix_group.move_to(LEFT * 3.1)

        self.play(Write(matrix_group))
        self.wait(pause_short)

        # ------------------------------------------------------------
        # Illustrate LD score for column 1
        # ------------------------------------------------------------
        col1_entries = get_column_entries(matrix, 0)

        self.play(*[entry.animate.set_color(highlight_color) for entry in col1_entries])
        self.wait(0.3)

        # Draw rectangle around column 1
        col1_rect = SurroundingRectangle(col1_entries, color=highlight_color, stroke_width=2)
        self.play(Create(col1_rect))
        self.wait(0.3)

        l1 = MathTex(r"\ell_1", r"=", font_size=42)
        l1.next_to(matrix_group, RIGHT, buff=1.0)
        l1.shift(UP * 1.2)

        term1 = MathTex(r"\rho_{11}^2", font_size=38, color=highlight_color)
        plus1 = MathTex(r"+", font_size=38)
        term2 = MathTex(r"\rho_{21}^2", font_size=38, color=highlight_color)
        plus2 = MathTex(r"+", font_size=38)
        term3 = MathTex(r"\rho_{31}^2", font_size=38, color=highlight_color)
        plus3 = MathTex(r"+", font_size=38)
        dots = MathTex(r"\cdots", font_size=38)
        plus4 = MathTex(r"+", font_size=38)
        term4 = MathTex(r"\rho_{M1}^2", font_size=38, color=highlight_color)

        expanded1 = VGroup(term1, plus1, term2, plus2, term3, plus3, dots, plus4, term4)
        expanded1.arrange(RIGHT, buff=0.14)
        expanded1.next_to(l1, RIGHT, buff=0.2)

        self.play(Write(l1), Write(VGroup(plus1, plus2, plus3, dots, plus4)))

        source_11 = get_entry(matrix, 0, 0)
        source_21 = get_entry(matrix, 1, 0)
        source_31 = get_entry(matrix, 2, 0)
        source_M1 = get_entry(matrix, 4, 0)

        # Term 1 appears with plus 1
        self.play(
            TransformFromCopy(source_11.copy(), term1),
            Write(plus1),
            run_time=0.5
        )
        
        # Term 2 appears with plus 2
        self.play(
            TransformFromCopy(source_21.copy(), term2),
            Write(plus2),
            run_time=0.5
        )
        
        # Term 3 appears with plus 3
        self.play(
            TransformFromCopy(source_31.copy(), term3),
            Write(plus3),
            run_time=0.5
        )
        
        # Dots appear with plus 4
        self.play(
            Write(dots),
            Write(plus4),
            run_time=0.5
        )
        
        # Final term
        self.play(
            TransformFromCopy(source_M1.copy(), term4),
            run_time=0.5
        )
        self.wait(pause_long)

        # ------------------------------------------------------------
        # Clear first-column illustration
        # ------------------------------------------------------------
        self.play(
            FadeOut(col1_rect),
            FadeOut(VGroup(l1, expanded1))
        )
        self.wait(0.15)

        # ------------------------------------------------------------
        # Illustrate LD score for column 2
        # ------------------------------------------------------------
        col2_entries = get_column_entries(matrix, 1)

        self.play(*[entry.animate.set_color(highlight_color) for entry in col2_entries])
        self.wait(0.3)

        # Draw rectangle around column 2
        col2_rect = SurroundingRectangle(col2_entries, color=highlight_color, stroke_width=2)
        self.play(Create(col2_rect))
        self.wait(0.3)

        l2 = MathTex(r"\ell_2", r"=", font_size=42)
        l2.next_to(matrix_group, RIGHT, buff=1.0)
        l2.shift(UP * 1.2)

        term1b = MathTex(r"\rho_{12}^2", font_size=38, color=highlight_color)
        plus1b = MathTex(r"+", font_size=38)
        term2b = MathTex(r"\rho_{22}^2", font_size=38, color=highlight_color)
        plus2b = MathTex(r"+", font_size=38)
        term3b = MathTex(r"\rho_{32}^2", font_size=38, color=highlight_color)
        plus3b = MathTex(r"+", font_size=38)
        dotsb = MathTex(r"\cdots", font_size=38)
        plus4b = MathTex(r"+", font_size=38)
        term4b = MathTex(r"\rho_{M2}^2", font_size=38, color=highlight_color)

        expanded2 = VGroup(term1b, plus1b, term2b, plus2b, term3b, plus3b, dotsb, plus4b, term4b)
        expanded2.arrange(RIGHT, buff=0.14)
        expanded2.next_to(l2, RIGHT, buff=0.2)

        self.play(Write(l2))

        source_12 = get_entry(matrix, 0, 1)
        source_22 = get_entry(matrix, 1, 1)
        source_32 = get_entry(matrix, 2, 1)
        source_M2 = get_entry(matrix, 4, 1)

        # Term 1 appears with plus 1
        self.play(
            TransformFromCopy(source_12.copy(), term1b),
            Write(plus1b),
            run_time=0.5
        )
        
        # Term 2 appears with plus 2
        self.play(
            TransformFromCopy(source_22.copy(), term2b),
            Write(plus2b),
            run_time=0.5
        )
        
        # Term 3 appears with plus 3
        self.play(
            TransformFromCopy(source_32.copy(), term3b),
            Write(plus3b),
            run_time=0.5
        )
        
        # Dots appear with plus 4
        self.play(
            Write(dotsb),
            Write(plus4b),
            run_time=0.5
        )
        
        # Final term
        self.play(
            TransformFromCopy(source_M2.copy(), term4b),
            run_time=0.5
        )
        self.wait(pause_long)

        # ------------------------------------------------------------
        # Return to the general equation
        # ------------------------------------------------------------
        self.play(
            FadeOut(col2_rect),
            FadeOut(VGroup(l2, expanded2)),
        )

        general_eq_final = MathTex(
            r"\ell_j = \sum_{k=1}^{M} \rho_{kj}^2",
            font_size=54,
            color=eq_color
        )
        general_eq_final.move_to(ORIGIN)

        self.play(
            FadeOut(matrix_group),
            Write(general_eq_final)
        )
        self.wait(2)