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

        # A short title helps orient the viewer before equations appear.
        title = Text("The variance sum law", font_size=42)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(pause_short)

        # Start with the general double-sum identity for any number of variables.
        eq_general = MathTex(
            r"\mathrm{Var}\!\left(\sum_{l=1}^{m} X_l\right)",
            r"=",
            r"\sum_{i=1}^{m}\sum_{j=1}^{m}\mathbf{X}_{ij}",
            font_size=44,
        )
        eq_general.move_to(DOWN * 2.2)
        self.play(Write(eq_general))
        self.wait(pause_long)

        # Introduce the covariance matrix directly, named bold X.
        x_matrix = MathTex(
            r"\mathbf{X}=",
            r"\begin{bmatrix}",
            r"\sigma_{\scriptscriptstyle 1}^{2}",
            r"&",
            r"\sigma_{\scriptscriptstyle 12}",
            r"\\",
            r"\sigma_{\scriptscriptstyle 12}",
            r"&",
            r"\sigma_{\scriptscriptstyle 2}^{2}",
            r"\end{bmatrix}",
            font_size=54,
        )
        x_matrix.move_to(UP * 0.9)

        # Persistent colors on matrix entries.
        x_matrix[2].set_color(variance_color)
        x_matrix[8].set_color(variance_color)
        x_matrix[4].set_color(covariance_color)
        x_matrix[6].set_color(covariance_color)

        self.play(FadeIn(x_matrix, shift=0.2 * DOWN), run_time=1.2)
        self.wait(pause_short)

        # Show matrix meaning in the lower equation area.
        var_1_box = SurroundingRectangle(x_matrix[2], color=variance_color, buff=0.1)
        var_2_box = SurroundingRectangle(x_matrix[8], color=variance_color, buff=0.1)
        var_label = Text("Diagonal: variances", font_size=34, color=variance_color)
        var_label.move_to(DOWN * 2.2)

        self.play(
            Create(var_1_box),
            Create(var_2_box),
            FadeOut(eq_general),
            FadeIn(var_label),
        )
        self.wait(pause_long)
        self.play(FadeOut(var_label), FadeOut(var_1_box), FadeOut(var_2_box))

        cov_12_box = SurroundingRectangle(x_matrix[4], color=covariance_color, buff=0.1)
        cov_21_box = SurroundingRectangle(x_matrix[6], color=covariance_color, buff=0.1)
        cov_label = Text("Off-diagonal: covariances", font_size=34, color=covariance_color)
        cov_label.move_to(DOWN * 2.2)

        self.play(
            Create(cov_12_box),
            Create(cov_21_box),
            FadeIn(cov_label),
        )
        self.wait(pause_long)
        self.play(FadeOut(cov_label), FadeOut(cov_12_box), FadeOut(cov_21_box))

        # Build the two-variable case in two grouped movements.
        eq_full = MathTex(
            r"\mathrm{Var}(X_1+X_2)",
            r"=",
            r"\sigma_{\scriptscriptstyle 1}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle 2}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle 12}",
            r"+",
            r"\sigma_{\scriptscriptstyle 12}",
            font_size=48,
        )
        eq_full.move_to(DOWN * 2.2)

        # Match destination colors so copied terms retain visual identity.
        eq_full[2].set_color(variance_color)
        eq_full[4].set_color(variance_color)
        eq_full[6].set_color(covariance_color)
        eq_full[8].set_color(covariance_color)

        self.play(Write(eq_full[0:2]))

        # Movement 1: both variance terms together.
        self.play(
            TransformFromCopy(x_matrix[2], eq_full[2]),
            Write(eq_full[3]),
            TransformFromCopy(x_matrix[8], eq_full[4]),
            run_time=1.3,
        )
        self.wait(pause_short)

        # Movement 2: both covariance terms together.
        self.play(
            Write(eq_full[5]),
            TransformFromCopy(x_matrix[4], eq_full[6]),
            Write(eq_full[7]),
            TransformFromCopy(x_matrix[6], eq_full[8]),
            run_time=1.3,
        )
        self.wait(pause_long)

        eq_simple = MathTex(
            r"\mathrm{Var}(X_1+X_2)",
            r"=",
            r"\sigma_{\scriptscriptstyle 1}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle 2}^{2}",
            r"+",
            r"2\sigma_{\scriptscriptstyle 12}",
            font_size=48,
        )
        eq_simple.move_to(eq_full)
        eq_simple[2].set_color(variance_color)
        eq_simple[4].set_color(variance_color)
        eq_simple[6].set_color(covariance_color)

        self.play(TransformMatchingTex(eq_full, eq_simple))
        self.wait(pause_long)

        # Connect back to the general law: m=2 is a special case.
        eq_special_case = MathTex(
            r"\mathrm{Var}(X_1+X_2)",
            r"=",
            r"\sum_{i=1}^{2}\sum_{j=1}^{2}\mathbf{X}_{ij}",
            r"=",
            r"\sigma_{\scriptscriptstyle 1}^{2}",
            r"+",
            r"\sigma_{\scriptscriptstyle 2}^{2}",
            r"+",
            r"2\sigma_{\scriptscriptstyle 12}",
            font_size=42,
        )
        eq_special_case.move_to(eq_simple)
        eq_special_case[4].set_color(variance_color)
        eq_special_case[6].set_color(variance_color)
        eq_special_case[8].set_color(covariance_color)
        self.play(TransformMatchingTex(eq_simple, eq_special_case), run_time=1.2)
        self.wait(2.8)

        self.play(
            FadeOut(x_matrix),
            FadeOut(title),
            eq_special_case.animate.move_to(ORIGIN).scale(1.06),
        )
        self.wait(3.0)
