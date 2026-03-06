"""
Minimal Manim scene for teaching the variance-of-a-sum identity.

This file is intentionally heavily commented for beginners.
"""

from manim import *

class VarianceOfSumScene(Scene):
    """
    A Scene is the basic Manim unit of animation.
    Manim calls construct() and renders everything we animate there.
    """

    def construct(self):
        # Hold times tuned for lecture pacing.
        pause_short = 1.2
        pause_long = 2.2

        # Color roles used consistently from matrix to equation.
        variance_color = YELLOW
        covariance_color = BLUE
        variable_index_color = ORANGE
        matrix_symbol_color = TEAL_B

        # A short title helps orient the viewer before equations appear.
        title = Text("The variance sum law", font_size=42)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(pause_short)

        # 1) Start from the familiar two-variable identity.
        eq_known = MathTex(
            r"\mathrm{Var}(X+Y)",
            r"=",
            r"\mathrm{Var}(X)",
            r"+",
            r"\mathrm{Var}(Y)",
            r"+",
            r"2\mathrm{Cov}(X,Y)",
            font_size=48,
        )
        eq_known.move_to(DOWN * 2.2)
        eq_known[2].set_color(variance_color)
        eq_known[4].set_color(variance_color)
        eq_known[6].set_color(covariance_color)
        self.play(Write(eq_known))
        self.wait(pause_long)

        # Switch to sigma notation before moving into the matrix entries.
        eq_sigma = MathTex(
            r"\mathrm{Var}(X+Y)",
            r"=",
            r"\sigma_{\scriptscriptstyle X}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle Y}^{2}",
            r"+",
            r"2\sigma_{\scriptscriptstyle XY}",
            font_size=48,
        )
        eq_sigma.move_to(eq_known)
        eq_sigma[2].set_color(variance_color)
        eq_sigma[4].set_color(variance_color)
        eq_sigma[6].set_color(covariance_color)
        self.play(TransformMatchingTex(eq_known, eq_sigma))
        self.wait(pause_short)

        # 2) Show the 2x2 covariance matrix and recover the same identity.
        sigma_matrix = MathTex(
            r"\mathbf{\Sigma}=",
            r"\begin{bmatrix}",
            r"\sigma_{\scriptscriptstyle X}^{2}",
            r"&",
            r"\sigma_{\scriptscriptstyle XY}",
            r"\\",
            r"\sigma_{\scriptscriptstyle XY}",
            r"&",
            r"\sigma_{\scriptscriptstyle Y}^{2}",
            r"\end{bmatrix}",
            font_size=54,
        )
        sigma_matrix.move_to(UP * 0.9)

        # Persistent colors on matrix entries.
        sigma_matrix[2].set_color(variance_color)
        sigma_matrix[8].set_color(variance_color)
        sigma_matrix[4].set_color(covariance_color)
        sigma_matrix[6].set_color(covariance_color)

        self.play(FadeIn(sigma_matrix, shift=0.2 * DOWN), run_time=1.2)
        self.wait(pause_short)
        self.play(FadeOut(eq_sigma))

        eq_from_matrix = MathTex(
            r"\mathrm{Var}(X+Y)",
            r"=",
            r"\sigma_{\scriptscriptstyle X}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle Y}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle XY}",
            r"+",
            r"\sigma_{\scriptscriptstyle XY}",
            font_size=48,
        )
        eq_from_matrix.move_to(DOWN * 2.2)
        eq_from_matrix[2].set_color(variance_color)
        eq_from_matrix[4].set_color(variance_color)
        eq_from_matrix[6].set_color(covariance_color)
        eq_from_matrix[8].set_color(covariance_color)

        self.play(Write(eq_from_matrix[0:2]))

        # First copy the diagonal entries (variances), then off-diagonals (covariances).
        self.play(
            TransformFromCopy(sigma_matrix[2], eq_from_matrix[2]),
            Write(eq_from_matrix[3]),
            TransformFromCopy(sigma_matrix[8], eq_from_matrix[4]),
            run_time=1.3,
        )
        self.wait(pause_short)

        self.play(
            Write(eq_from_matrix[5]),
            TransformFromCopy(sigma_matrix[4], eq_from_matrix[6]),
            Write(eq_from_matrix[7]),
            TransformFromCopy(sigma_matrix[6], eq_from_matrix[8]),
            run_time=1.3,
        )
        self.wait(pause_long)

        self.play(TransformMatchingTex(eq_from_matrix, eq_sigma))
        self.wait(pause_short)

        # 3) Generalize: summing all entries of the covariance matrix.
        eq_two_sum = MathTex(
            r"\mathrm{Var}(X+Y)",
            r"=",
            r"\sum_{i=1}^{2}\sum_{j=1}^{2}\mathbf{\Sigma}_{ij}",
            font_size=42,
        )
        eq_two_sum.move_to(DOWN * 2.2)
        self.play(TransformMatchingTex(eq_sigma, eq_two_sum), run_time=1.1)
        self.wait(pause_short)

        eq_general = MathTex(
            r"\mathrm{Var}\!\left(\sum_{l=1}^{m}",
            r"X_l",
            r"\right)",
            r"=",
            r"\sum_{i=1}^{m}\sum_{j=1}^{m}",
            r"\mathbf{\Sigma}_{ij}",
            font_size=44,
        )
        eq_general.move_to(eq_two_sum)
        eq_general[1].set_color(variable_index_color)
        eq_general[5].set_color(matrix_symbol_color)
        self.play(TransformMatchingTex(eq_two_sum, eq_general), run_time=1.2)
        self.wait(pause_short)

        # Expand the visual from 2x2 to a larger m x m covariance matrix.
        sigma_matrix_large = MathTex(
            r"\mathbf{\Sigma}=",
            r"\begin{bmatrix}",
            r"\sigma_{\scriptscriptstyle 11}",
            r"&",
            r"\sigma_{\scriptscriptstyle 12}",
            r"&",
            r"\cdots",
            r"&",
            r"\sigma_{\scriptscriptstyle 1m}",
            r"\\",
            r"\sigma_{\scriptscriptstyle 21}",
            r"&",
            r"\sigma_{\scriptscriptstyle 22}",
            r"&",
            r"\cdots",
            r"&",
            r"\sigma_{\scriptscriptstyle 2m}",
            r"\\",
            r"\vdots",
            r"&",
            r"\vdots",
            r"&",
            r"\ddots",
            r"&",
            r"\vdots",
            r"\\",
            r"\sigma_{\scriptscriptstyle m1}",
            r"&",
            r"\sigma_{\scriptscriptstyle m2}",
            r"&",
            r"\cdots",
            r"&",
            r"\sigma_{\scriptscriptstyle mm}",
            r"\end{bmatrix}",
            font_size=42,
        )
        sigma_matrix_large.move_to(sigma_matrix)
        self.play(TransformMatchingTex(sigma_matrix, sigma_matrix_large), run_time=1.2)
        sigma_matrix = sigma_matrix_large
        self.wait(pause_short)

        sum_caption = Text(
            "Same idea: add every element in the covariance matrix.",
            font_size=30,
        )
        sum_caption.next_to(eq_general, UP, buff=0.8)
        self.play(FadeIn(sum_caption))
        self.wait(pause_long)

        x_symbol_box = SurroundingRectangle(eq_general[5], color=matrix_symbol_color, buff=0.08)
        matrix_symbol = MathTex(r"\mathbf{\Sigma}", font_size=38, color=matrix_symbol_color)
        matrix_text = Text("is the covariance matrix.", font_size=28)
        x_symbol_label = VGroup(matrix_symbol, matrix_text).arrange(RIGHT, buff=0.2)
        x_symbol_label.next_to(eq_general, UP, buff=0.8).align_to(eq_general, RIGHT)
        x_symbol_arrow = Arrow(
            x_symbol_label.get_bottom(),
            eq_general[5].get_top(),
            buff=0.08,
            stroke_width=4,
            color=matrix_symbol_color,
            max_tip_length_to_length_ratio=0.2,
        )
        self.play(
            FadeOut(sum_caption),
            Create(x_symbol_box),
            FadeIn(x_symbol_label),
            GrowArrow(x_symbol_arrow),
        )
        self.wait(pause_short)
        self.play(FadeOut(x_symbol_box), FadeOut(x_symbol_label), FadeOut(x_symbol_arrow))

        self.play(
            FadeOut(sigma_matrix),
            FadeOut(title),
            eq_general.animate.move_to(ORIGIN).scale(1.06),
        )
        self.wait(3.0)
