
"""
Manim scene for teaching Mendelian inheritance and parent-offspring resemblance.

This file is intentionally written for a beginner-friendly workflow:
1. Edit the example haplotypes or timings below.
2. Render a quick draft while you are iterating.
3. Render a higher-quality version when the pacing feels right.

Common render commands from the project root:
    manim -pql manim/mendelian_inheritance_v2.py MendelianInheritanceScene
    python -m manim -pql manim/mendelian_inheritance_v2.py MendelianInheritanceScene
    py -m manim -pql manim/mendelian_inheritance_v2.py MendelianInheritanceScene

Higher quality:
    manim -pqh manim/mendelian_inheritance_v2.py MendelianInheritanceScene

To export multiple MP4 files at explicit cut points (for slide-by-slide playback):
    manim --save_sections --format=mp4 --fps 30 -r 1280,720 \
        manim/mendelian_inheritance_v2.py MendelianInheritanceScene
"""

from manim import *
import numpy as np


# ---------------------------------------------------------------------------
# Top-level configuration block
# ---------------------------------------------------------------------------
# These arrays define the worked example shown in the animation.
# The parent carries two homologous haplotypes, each coded as a row of 0/1 alleles.
# We deliberately include loci with genotype counts 0, 1, and 2 so that the
# viewer can see both deterministic transmission and random transmission.
PARENT_HAPLOTYPE_1 = [1, 0, 1, 1, 0, 0]
PARENT_HAPLOTYPE_2 = [0, 1, 1, 0, 1, 0]

# Each entry says which parental haplotype contributes the allele to the gamete.
# 0 means "take the allele from haplotype 1" and 1 means "take it from haplotype 2".
# This fixed pattern keeps the rendered animation reproducible.
TRANSMISSION_PATTERN = [0, 1, 0, 1, 1, 0]

# Worked maternal example for the post-case-summary section.
MOTHER_HAPLOTYPE_1 = [1, 1, 0, 0, 1, 0]
MOTHER_HAPLOTYPE_2 = [0, 1, 0, 1, 1, 1]
MATERNAL_TRANSMISSION_PATTERN = [1, 0, 1, 1, 0, 0]

# Symbolic additive effects. These are not numerically used in the animation,
# but keeping them explicit in the code helps show where the weighted sums come from.
ALLELE_EFFECT_LABELS = [r"\beta_1", r"\beta_2", r"\beta_3", r"\beta_4", r"\beta_5", r"\beta_6"]

# Timing is separated from the animation logic so you can later slow down or
# speed up the lecture without rewriting the teaching structure.
TIMING = {
    "short_pause": 1.2,
    "medium_pause": 2.0,
    "long_pause": 3.0,
    "locus_animation": 0.5,
}

# Color roles are named semantically rather than by object, which makes the
# file easier to extend later when you add assortative mating or LD material.
COLORS = {
    "haplotype_1": BLUE_E,
    "haplotype_2": TEAL_E,
    "genotype": ORANGE,
    "gamete": GREEN_E,
    "segregation": PURPLE_B,
    "highlight": YELLOW,
    "assumption": GREY_B,
    "muted": GREY_C,
    "title": WHITE,
}

# Layout constants are grouped here so the spatial structure stays stable.
# A later extension could reuse the same left-side "genome panel" and simply
# swap in new transmission logic or new summary equations.
LAYOUT = {
    "cells_center_x": -1.0,
    "label_buffer": 0.45,
    "cell_gap": 0.14,
    "cell_width": 0.78,
    "cell_height": 0.58,
    "locus_label_y_offset": 0.28,
    "right_panel_center": np.array([3.85, 0.9, 0.0]),
    "transmission_panel_center": np.array([3.1, 0.9, 0.0]),
    "summary_center": np.array([0.0, 0.15, 0.0]),
}

# When True, calls to self.mark_video_split(...) create new section files
# (only when Manim is rendered with --save_sections).
# Set this to False if you want one continuous movie again.
ENABLE_VIDEO_SPLITS = True

def compute_genotype_counts(haplotype_1, haplotype_2):
    """Return x_{jp}, the parent's genotype count at each locus."""
    return [upper + lower for upper, lower in zip(haplotype_1, haplotype_2)]


def compute_transmitted_alleles(haplotype_1, haplotype_2, transmission_pattern):
    """Return z_{jp}, the allele transmitted by the focal parent at each locus."""
    transmitted = []
    for upper, lower, chosen_haplotype in zip(
        haplotype_1, haplotype_2, transmission_pattern
    ):
        transmitted.append(upper if chosen_haplotype == 0 else lower)
    return transmitted


def compute_segregation_deviations(genotype_counts, transmitted_alleles):
    r"""Return e_j = z_{jp} - (1/2) x_{jp}."""
    return [transmitted - 0.5 * genotype for genotype, transmitted in zip(genotype_counts, transmitted_alleles)]


class MendelianInheritanceScene(Scene):
    """
    One master scene made of pedagogical sections.

    The scene is modular in the sense that each conceptual section lives in a
    separate method, and the data-generating logic is separated from the
    drawing logic. That makes it easier to later adapt the code for:
    - assortative mating
    - linkage disequilibrium
    - multiple parents or multiple offspring
    """

    def construct(self):
        # -------------------------------------------------------------------
        # Prepare data once at the start.
        # -------------------------------------------------------------------
        self.haplotype_1 = PARENT_HAPLOTYPE_1
        self.haplotype_2 = PARENT_HAPLOTYPE_2
        self.transmission_pattern = TRANSMISSION_PATTERN
        self.mother_haplotype_1 = MOTHER_HAPLOTYPE_1
        self.mother_haplotype_2 = MOTHER_HAPLOTYPE_2
        self.maternal_transmission_pattern = MATERNAL_TRANSMISSION_PATTERN
        self.effect_labels = ALLELE_EFFECT_LABELS

        self.genotype_counts = compute_genotype_counts(self.haplotype_1, self.haplotype_2)
        self.transmitted_alleles = compute_transmitted_alleles(
            self.haplotype_1,
            self.haplotype_2,
            self.transmission_pattern,
        )
        self.segregation_deviations = compute_segregation_deviations(
            self.genotype_counts,
            self.transmitted_alleles,
        )

        self.maternal_genotype_counts = compute_genotype_counts(
            self.mother_haplotype_1,
            self.mother_haplotype_2,
        )
        self.maternal_transmitted_alleles = compute_transmitted_alleles(
            self.mother_haplotype_1,
            self.mother_haplotype_2,
            self.maternal_transmission_pattern,
        )
        self.maternal_segregation_deviations = compute_segregation_deviations(
            self.maternal_genotype_counts,
            self.maternal_transmitted_alleles,
        )

        self.offspring_genotype_counts = [
            paternal + maternal
            for paternal, maternal in zip(
                self.transmitted_alleles,
                self.maternal_transmitted_alleles,
            )
        ]

        # Build recurring layout objects once.
        self.build_static_layout()

        # Teaching flow.
        self.play_parent_intro()
        self.play_gamete_formation()

        self.mark_video_split("part_02_decomposition_to_summary")

        self.play_locus_decomposition()
        self.play_additive_value_aggregation()

    # -----------------------------------------------------------------------
    # General helper methods
    # -----------------------------------------------------------------------
    def mark_video_split(self, section_name):
        """
        Start a new output section if splitting is enabled.

        Practical use:
        1) Place this call exactly where you want the NEXT video file to start.
        2) Render with --save_sections.
        3) Manim writes one MP4 per section, which is ideal for click-to-advance slides.
        """
        if ENABLE_VIDEO_SPLITS:
            self.next_section(section_name)

    def make_value_cell(
        self,
        value,
        box_color,
        fill_opacity=0.18,
        font_size=30,
    ):
        """
        Build one boxed allele/count cell.

        We keep each cell as a small dictionary so later code can address:
        - the rectangle itself (for highlighting)
        - the entry text (for copying into equations or gametes)
        - the grouped cell (for layout)
        """
        box = RoundedRectangle(
            corner_radius=0.08,
            width=LAYOUT["cell_width"],
            height=LAYOUT["cell_height"],
            stroke_color=box_color,
            stroke_width=2.0,
            fill_color=box_color,
            fill_opacity=fill_opacity,
        )

        entry = None
        if value is not None:
            entry = MathTex(str(value), font_size=font_size)
            entry.move_to(box.get_center())
        else:
            # A blank cell is still useful as a visual destination for the gamete.
            entry = VectorizedPoint(box.get_center())

        group = VGroup(box, entry)
        return {"box": box, "entry": entry, "group": group, "value": value}

    def build_row(self, values, label_tex, box_color):
        """
        Build one labeled row of boxes.

        Rows are used for:
        - the two parental haplotypes
        - genotype counts x_{jp}
        - transmitted alleles z_j
        """
        label = MathTex(label_tex, font_size=32)
        label.set_color(box_color)

        cell_items = [self.make_value_cell(value, box_color) for value in values]
        cells_group = VGroup(*[cell["group"] for cell in cell_items]).arrange(
            RIGHT,
            buff=LAYOUT["cell_gap"],
        )

        return {
            "label": label,
            "cells": cell_items,
            "cells_group": cells_group,
            "group": VGroup(label, cells_group),
        }

    def position_row(self, row, y_coordinate):
        """Place a row so that all rows share the same aligned locus positions."""
        row["cells_group"].move_to(np.array([LAYOUT["cells_center_x"], y_coordinate, 0.0]))
        row["label"].next_to(row["cells_group"], LEFT, buff=LAYOUT["label_buffer"])
        row["group"] = VGroup(row["label"], row["cells_group"])

    def build_locus_labels(self, reference_row):
        """Create one label above each locus."""
        labels = VGroup()
        for locus_index, cell in enumerate(reference_row["cells"], start=1):
            label = MathTex(fr"j={locus_index}", font_size=24)
            label.next_to(cell["box"], UP, buff=LAYOUT["locus_label_y_offset"])
            labels.add(label)
        return labels

    def make_right_panel_note(self, *lines, center=None):
        """
        Create a note in the fixed right-side teaching area.

        Using a single right panel keeps the left-side genome panel stable, which
        matters a lot for pedagogy: students should not spend attention on
        moving objects when the conceptual point is elsewhere.
        """
        note_lines = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        background = BackgroundRectangle(
            note_lines,
            buff=0.2,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        panel = VGroup(background, note_lines)
        note_center = LAYOUT["right_panel_center"] if center is None else center
        panel.move_to(note_center)
        return panel

    def column_group(self, locus_index, include_gamete=True):
        """Return the stack of cells in one locus column."""
        column_items = [
            self.haplotype_row_1["cells"][locus_index]["group"],
            self.haplotype_row_2["cells"][locus_index]["group"],
            self.genotype_row["cells"][locus_index]["group"],
        ]
        if include_gamete:
            column_items.append(self.gamete_row["cells"][locus_index]["group"])
        return VGroup(*column_items)

    def create_gamete_entry(self, locus_index, value):
        """
        Fill one previously blank gamete cell.

        We create the text on demand rather than upfront so the transmitted
        allele visibly appears only when that locus is animated.
        """
        target_cell = self.gamete_row["cells"][locus_index]
        target_entry = MathTex(str(value), font_size=30)
        target_entry.move_to(target_cell["box"].get_center())
        target_cell["group"].remove(target_cell["entry"])
        target_cell["entry"] = target_entry
        target_cell["group"].add(target_entry)
        return target_entry

    def color_equation(self, equation):
        """
        Apply a consistent color language across equations.

        This is intentionally simple: a few repeated colors are easier for the
        audience to learn than many one-off highlighting schemes.
        """
        equation.set_color_by_tex(r"x_{jp}", COLORS["genotype"])
        equation.set_color_by_tex(r"x_{jm}", COLORS["haplotype_2"])
        equation.set_color_by_tex(r"x_{jo}", COLORS["gamete"])
        equation.set_color_by_tex(r"z_{jp}", COLORS["gamete"])
        equation.set_color_by_tex(r"z_{jm}", COLORS["haplotype_2"])
        equation.set_color_by_tex(r"\epsilon", COLORS["segregation"])
        equation.set_color_by_tex(r"e_j", COLORS["segregation"])
        equation.set_color_by_tex(r"e_{j1}", COLORS["segregation"])
        equation.set_color_by_tex(r"e_{j2}", COLORS["segregation"])
        equation.set_color_by_tex(r"e_{jm}", COLORS["segregation"])
        equation.set_color_by_tex(r"e_{jp}", COLORS["segregation"])
        return equation

    def build_static_layout(self):
        """Build the rows and reusable layout objects that persist across sections."""
        self.haplotype_row_1 = self.build_row(
            self.haplotype_1,
            r"\text{haplotype }h_{j1}",
            COLORS["haplotype_1"],
        )
        self.haplotype_row_2 = self.build_row(
            self.haplotype_2,
            r"\text{haplotype }h_{j2}",
            COLORS["haplotype_2"],
        )
        self.genotype_row = self.build_row(
            self.genotype_counts,
            r"\text{genotype }x_{jp}",
            COLORS["genotype"],
        )

        self.gamete_row = self.build_row(
            [None] * len(self.haplotype_1),
            r"\text{haplotype }z_{jp}",
            COLORS["gamete"],
        )

        self.maternal_transmitted_row = self.build_row(
            self.maternal_transmitted_alleles,
            r"\text{haplotype }z_{jm}",
            COLORS["haplotype_2"],
        )
        self.maternal_genotype_row = self.build_row(
            self.maternal_genotype_counts,
            r"\text{genotype }x_{jm}",
            COLORS["haplotype_2"],
        )

        self.offspring_row = self.build_row(
            [None] * len(self.haplotype_1),
            r"\text{genotype }x_{jo}",
            COLORS["genotype"],
        )

        # Initial (pre-mother) placement.
        self.position_row(self.haplotype_row_1, 1.45)
        self.position_row(self.haplotype_row_2, 0.55)
        self.position_row(self.genotype_row, -0.45)
        self.position_row(self.gamete_row, -2.0)

        # Final-placement rows are positioned here and revealed in Section 4.
        self.position_row(self.maternal_transmitted_row, -0.95)
        self.position_row(self.maternal_genotype_row, -1.9)
        self.position_row(self.offspring_row, -2.85)

        self.locus_labels = self.build_locus_labels(self.haplotype_row_1)

        haplotype_cells = VGroup(
            self.haplotype_row_1["cells_group"],
            self.haplotype_row_2["cells_group"],
        )
        self.haplotype_brace = Brace(haplotype_cells, RIGHT, buff=0.18)
        self.haplotype_brace_label = self.haplotype_brace.get_text(
            "two homologous haplotypes",
            buff=0.12,
        )
        self.haplotype_brace_label.scale(0.5)

        self.parent_group = VGroup(
            self.locus_labels,
            self.haplotype_row_1["group"],
            self.haplotype_row_2["group"],
            self.genotype_row["group"],
            self.gamete_row["group"],
            self.maternal_transmitted_row["group"],
            self.maternal_genotype_row["group"],
            self.offspring_row["group"],
        )

    # -----------------------------------------------------------------------
    # Section 1: introduce the diploid parent genotype
    # -----------------------------------------------------------------------
    def play_parent_intro(self):
        self.wait(TIMING["short_pause"] * 0.6)

        self.play(
            LaggedStart(*[Write(label) for label in self.locus_labels], lag_ratio=0.08),
            run_time=1.2,
        )
        self.play(
            FadeIn(self.haplotype_row_1["group"], shift=0.15 * RIGHT),
            FadeIn(self.haplotype_row_2["group"], shift=0.15 * RIGHT),
            run_time=1.1,
        )
        self.wait(TIMING["short_pause"])

        self.play(
            Create(self.haplotype_brace),
            FadeIn(self.haplotype_brace_label, shift=0.1 * RIGHT),
            run_time=1.0,
        )
        self.wait(TIMING["medium_pause"])
        self.play(FadeOut(self.haplotype_brace_label), FadeOut(self.haplotype_brace), run_time=0.7)

        genotype_formula = self.color_equation(
            MathTex(
                r"x_{jp}",
                r"=",
                r"h_{j1}",
                r"+",
                r"h_{j2}",
                font_size=38,
            )
        )
        genotype_formula.scale(0.9)
        genotype_formula.move_to(np.array([3.35, -0.35, 0.0]))

        example_highlight = SurroundingRectangle(
            self.column_group(0, include_gamete=False),
            color=COLORS["highlight"],
            buff=0.12,
        )
        example_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"1+0=1", font_size=36)),
        )

        self.play(FadeIn(self.genotype_row["group"], shift=0.15 * RIGHT))
        self.play(Create(example_highlight), FadeIn(example_note), Write(genotype_formula))
        self.wait(TIMING["medium_pause"])
        self.play(FadeOut(example_highlight), FadeOut(example_note))

        self.genotype_formula = genotype_formula

    # -----------------------------------------------------------------------
    # Section 2: show locus-by-locus gamete formation
    # -----------------------------------------------------------------------
    def play_gamete_formation(self):
        self.play(FadeIn(self.gamete_row["group"], shift=0.12 * RIGHT), run_time=0.5)
        self.wait(0.4)

        for locus_index, (transmitted_value, chosen_haplotype) in enumerate(
            zip(
                self.transmitted_alleles,
                self.transmission_pattern,
            )
        ):

            column_highlight = SurroundingRectangle(
                self.column_group(locus_index, include_gamete=False),
                color=COLORS["highlight"],
                buff=0.10,
            )

            source_row = self.haplotype_row_1 if chosen_haplotype == 0 else self.haplotype_row_2
            source_cell = source_row["cells"][locus_index]
            target_cell = self.gamete_row["cells"][locus_index]

            source_highlight = SurroundingRectangle(
                source_cell["box"],
                color=COLORS["gamete"],
                buff=0.07,
            )
            target_highlight = SurroundingRectangle(
                target_cell["box"],
                color=COLORS["gamete"],
                buff=0.07,
            )

            transmitted_arrow = Arrow(
                source_cell["box"].get_bottom(),
                target_cell["box"].get_top(),
                buff=0.08,
                stroke_width=4,
                color=COLORS["gamete"],
                max_tip_length_to_length_ratio=0.18,
            )

            target_entry = MathTex(str(transmitted_value), font_size=30)
            target_entry.move_to(target_cell["box"].get_center())

            self.play(Create(column_highlight), run_time=0.20)
            self.play(Create(source_highlight), Create(target_highlight), run_time=0.18)
            self.play(GrowArrow(transmitted_arrow), run_time=0.18)
            self.play(
                TransformFromCopy(source_cell["entry"], target_entry),
                run_time=0.35,
            )

            target_cell["group"].remove(target_cell["entry"])
            target_cell["entry"] = target_entry
            target_cell["group"].add(target_entry)

            self.play(
                FadeOut(column_highlight),
                FadeOut(source_highlight),
                FadeOut(target_highlight),
                FadeOut(transmitted_arrow),
                run_time=0.15,
            )

        self.wait(TIMING["short_pause"])

        self.transmitted_brace = Brace(self.gamete_row["cells_group"], DOWN, buff=0.18)
        self.transmitted_brace_label = self.transmitted_brace.get_text(
            "offspring haplotype",
            buff=0.1,
        )
        self.transmitted_brace_label.scale(0.48)

        offspring_haplotype_formula = self.color_equation(
            MathTex(r"z_{jp}=\tfrac{1}{2}x_{jp}+e_j", font_size=36)
        )
        offspring_haplotype_formula.move_to(np.array([3.35, -2.0, 0.0]))

        self.play(
            Create(self.transmitted_brace),
            FadeIn(self.transmitted_brace_label, shift=0.1 * DOWN),
            Write(offspring_haplotype_formula),
            run_time=0.8,
        )
        self.wait(TIMING["short_pause"])

        self.offspring_haplotype_formula = offspring_haplotype_formula

    # -----------------------------------------------------------------------
    # Section 3: connect a transmitted allele to 1/2 x_{jp} + \epsilon_j
    # -----------------------------------------------------------------------
    def play_locus_decomposition(self):
        paternal_panel_objects = VGroup(
            self.haplotype_row_1["group"],
            self.haplotype_row_2["group"],
            self.locus_labels,
            self.haplotype_brace_label,
            self.haplotype_brace,
        )

        self.play(FadeOut(paternal_panel_objects), run_time=0.8)

        case_summary = VGroup(
            self.color_equation(MathTex(r"x_{jp}=0 \Rightarrow z_{jp}=0,\ e_j=0", font_size=30)),
            self.color_equation(MathTex(r"x_{jp}=2 \Rightarrow z_{jp}=1,\ e_j=0", font_size=30)),
            self.color_equation(
                MathTex(
                    r"x_{jp}=1 \Rightarrow z_{jp}\in\{0,1\},\ e_j\in\{-\tfrac{1}{2},+\tfrac{1}{2}\}",
                    font_size=30,
                )
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.20)

        case_box = BackgroundRectangle(
            case_summary,
            buff=0.22,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        case_panel = VGroup(case_box, case_summary)
        case_panel.move_to(np.array([0.0, 0.2, 0.0]))

        self.play(FadeIn(case_panel, shift=0.12 * UP), run_time=0.9)
        self.wait(TIMING["long_pause"])

        self.mark_video_split("part_03_after_case_summary")
        self.case_panel = case_panel

    # -----------------------------------------------------------------------
    # Section 4: combine parental transmissions at locus j
    # -----------------------------------------------------------------------
    def play_additive_value_aggregation(self):
        self.play(
            FadeOut(self.case_panel),
            FadeOut(self.genotype_formula),
            FadeOut(self.transmitted_brace),
            FadeOut(self.transmitted_brace_label),
            FadeOut(self.offspring_haplotype_formula),
            run_time=0.8,
        )

        # Target order:
        # x_{jp}, z_{jp}, x_{jo}, z_{jm}, x_{jm}
        targets = {
            "x_jp": 1.4,
            "z_jp": 0.55,
            "x_jo": -0.30,
            "z_jm": -1.15,
            "x_jm": -2.0,
        }

        shifts = {
            "x_jp": targets["x_jp"] - self.genotype_row["cells_group"].get_center()[1],
            "z_jp": targets["z_jp"] - self.gamete_row["cells_group"].get_center()[1],
            "x_jo": targets["x_jo"] - self.offspring_row["cells_group"].get_center()[1],
            "z_jm": targets["z_jm"] - self.maternal_transmitted_row["cells_group"].get_center()[1],
            "x_jm": targets["x_jm"] - self.maternal_genotype_row["cells_group"].get_center()[1],
        }

        # Move hidden rows to their target y-positions before revealing them.
        self.offspring_row["group"].shift(UP * shifts["x_jo"])
        self.maternal_transmitted_row["group"].shift(UP * shifts["z_jm"])
        self.maternal_genotype_row["group"].shift(UP * shifts["x_jm"])

        self.play(
            self.genotype_row["group"].animate.shift(UP * shifts["x_jp"]),
            self.gamete_row["group"].animate.shift(UP * shifts["z_jp"]),
            FadeIn(self.offspring_row["group"], shift=0.12 * UP),
            FadeIn(self.maternal_transmitted_row["group"], shift=0.12 * UP),
            FadeIn(self.maternal_genotype_row["group"], shift=0.12 * UP),
            run_time=1.0,
        )
        self.wait(TIMING["medium_pause"])

        combine_heading = self.color_equation(MathTex(r"x_{jo}=z_{jp}+z_{jm}", font_size=40))
        combine_heading.move_to(np.array([3.65, 1.15, 0.0]))

        self.play(Write(combine_heading), run_time=0.8)

        for locus_index, offspring_value in enumerate(self.offspring_genotype_counts):
            column_highlight = SurroundingRectangle(
                VGroup(
                    self.gamete_row["cells"][locus_index]["box"],
                    self.offspring_row["cells"][locus_index]["box"],
                    self.maternal_transmitted_row["cells"][locus_index]["box"],
                ),
                color=COLORS["highlight"],
                buff=0.1,
            )

            target_cell = self.offspring_row["cells"][locus_index]
            target_entry = MathTex(str(offspring_value), font_size=30)
            target_entry.move_to(target_cell["box"].get_center())

            source_pair = VGroup(
                self.gamete_row["cells"][locus_index]["entry"],
                self.maternal_transmitted_row["cells"][locus_index]["entry"],
            )

            self.play(Create(column_highlight), run_time=0.22)
            self.play(TransformFromCopy(source_pair, target_entry), run_time=TIMING["locus_animation"])

            target_cell["group"].remove(target_cell["entry"])
            target_cell["entry"] = target_entry
            target_cell["group"].add(target_entry)

            self.play(FadeOut(column_highlight), run_time=0.18)

        self.wait(TIMING["medium_pause"])

        # Once x_{jo} is formed, the two haplotype rows can be removed.
        self.play(
            FadeOut(self.gamete_row["group"]),
            FadeOut(self.maternal_transmitted_row["group"]),
            run_time=0.7,
        )
        self.remove(
            *[cell["entry"] for cell in self.gamete_row["cells"]],
            *[cell["entry"] for cell in self.maternal_transmitted_row["cells"]],
        )

        final_relation = self.color_equation(
            MathTex(r"x_{jo}=\tfrac{1}{2}x_{jp}+\epsilon", font_size=40)
        )
        final_relation.move_to(combine_heading)

        epsilon_definition = self.color_equation(
            MathTex(r"\epsilon=\tfrac{1}{2}x_{jm}+e_{jm}+e_{jp}", font_size=34)
        )
        epsilon_definition.next_to(final_relation, DOWN, aligned_edge=LEFT, buff=0.28)

        self.play(
            TransformMatchingTex(
                combine_heading,
                final_relation,
                replace_mobject_with_target_in_scene=True,
            ),
            FadeIn(epsilon_definition),
            run_time=1.0,
        )
        self.wait(TIMING["long_pause"])

    # -----------------------------------------------------------------------
    # Section 5: show Cov(x_{jp}, x_{jo}) at locus j
    # -----------------------------------------------------------------------
    def play_correlation_summary(self):
        """Covariance derivation moved to slides; kept as a placeholder."""
        return
