"""
Manim scene for teaching how assortative mating induces covariance in causes.

This file is intentionally written in the same beginner-friendly spirit as
`mendelian_inheritance_v2.py`:
1. Edit the deterministic example at the top.
2. Render a quick draft while tuning spacing or pacing.
3. Render a higher-quality version once the lecture flow feels right.

Common render commands from the project root:
    manim -pql manim/assortment_v2.py AssortmentCausesScene
    python -m manim -pql manim/assortment_v2.py AssortmentCausesScene

Higher quality:
    manim -pqh manim/assortment_v2.py AssortmentCausesScene

To export multiple MP4 files at explicit cut points:
    manim --save_sections --format=mp4 --fps 30 -r 1280,720 \
        manim/assortment_v2.py AssortmentCausesScene

Note:
    In this local environment, `python` or `manim` may not be on PATH.
    If so, run the same command with the explicit Python interpreter that has
    Manim installed.
"""

from manim import *
import numpy as np


# ---------------------------------------------------------------------------
# Top-level configuration block
# ---------------------------------------------------------------------------
# The animation uses a fixed deterministic example so the sorting pattern is
# reproducible and easy to adjust later.
N_ROWS = 16

# Maternal-side component values. They are monotone in the underlying example,
# but the scene starts from an unsorted display order.
MATERNAL_G_VALUES = [
    0.4,
    0.5,
    0.6,
    0.8,
    0.9,
    1.0,
    1.1,
    1.2,
    1.4,
    1.5,
    1.6,
    1.8,
    1.9,
    2.1,
    2.2,
    2.4,
]

MATERNAL_E_VALUES = [
    0.5,
    0.6,
    0.6,
    0.7,
    0.8,
    0.8,
    0.9,
    1.0,
    1.0,
    1.1,
    1.2,
    1.2,
    1.3,
    1.4,
    1.5,
    1.6,
]

PATERNAL_G_VALUES = [
    0.3,
    0.5,
    0.6,
    0.7,
    0.8,
    1.0,
    1.1,
    1.2,
    1.3,
    1.5,
    1.6,
    1.7,
    1.9,
    2.0,
    2.1,
    2.3,
]

PATERNAL_E_VALUES = [
    0.6,
    0.6,
    0.7,
    0.7,
    0.8,
    0.8,
    0.9,
    0.9,
    1.0,
    1.0,
    1.1,
    1.2,
    1.2,
    1.3,
    1.4,
    1.5,
]

# The visual story starts from these fixed unsorted orders on the two sides.
MATERNAL_UNSORTED_ORDER = [7, 1, 12, 4, 15, 0, 10, 3, 14, 6, 9, 2, 13, 5, 11, 8]
PATERNAL_UNSORTED_ORDER = [5, 14, 2, 11, 0, 9, 15, 4, 12, 1, 8, 6, 13, 3, 10, 7]

# Timing stays separate from animation logic so the lecture can later be sped
# up or slowed down without rewriting the teaching structure.
TIMING = {
    "short_pause": 1.0,
    "medium_pause": 1.8,
    "long_pause": 2.8,
    "sorting": 1.7,
    "highlight": 0.8,
}

# Semantic color names matter here because the audience is learning a small
# visual language repeatedly across equations and objects.
COLORS = {
    "phenotype": WHITE,
    "genetic": GREEN_E,
    "environment": ORANGE,
    "support": BLUE_B,
    "highlight": YELLOW,
    "cross_term": PURPLE_B,
    "band_high": GOLD_E,
    "band_mid": BLUE_E,
    "band_low": TEAL_E,
    "muted": GREY_C,
    "title": WHITE,
}

# The left side hosts the sortable columns.
# Once the phenotype columns disappear, the equations move closer to center.
LAYOUT = {
    "left_triplet_center_x": -2.75,
    "right_triplet_center_x": 0.65,
    "top_row_y": 2.45,
    "row_step": 0.33,
    "header_y": 3.02,
    "cell_width": 0.72,
    "cell_height": 0.26,
    "cell_gap": 0.20,
    "cell_font_size": 20,
    "header_font_size": 25,
    "component_muted_opacity": 0.34,
    "band_buff": 0.06,
    "right_panel_center": np.array([4.40, 0.8, 0.0]),
    "right_panel_max_width": 4.55,
    "equation_panel_center": np.array([3.45, 0.82, 0.0]),
}

ENABLE_VIDEO_SPLITS = True


def format_decimal(value):
    """Return one decimal place for the teaching display."""
    return f"{value:.1f}"


def build_people(prefix, g_values, e_values):
    """
    Build the deterministic row data used by the animation.

    The returned list is the underlying data order, not the on-screen order.
    Sorting order is handled separately so the scene can animate the movement.
    """
    people = []
    for index, (g_value, e_value) in enumerate(zip(g_values, e_values), start=1):
        people.append(
            {
                "id": f"{prefix}{index:02d}",
                "g": g_value,
                "e": e_value,
                "y": g_value + e_value,
            }
        )
    return people


class AssortmentCausesScene(Scene):
    """
    Teaching scene for the covariance-of-sums view of assortative mating.

    The scope is intentionally narrow:
    - sort on phenotype
    - show that the causes move with the sorted people
    - expand the partner covariance using the covariance-of-sums law
    - stop after substituting g_i = sum_j beta_j x_ij
    """

    def construct(self):
        # -------------------------------------------------------------------
        # Prepare data once at the top.
        # -------------------------------------------------------------------
        self.maternal_people = build_people("m", MATERNAL_G_VALUES, MATERNAL_E_VALUES)
        self.paternal_people = build_people("p", PATERNAL_G_VALUES, PATERNAL_E_VALUES)

        self.maternal_unsorted_order = MATERNAL_UNSORTED_ORDER
        self.paternal_unsorted_order = PATERNAL_UNSORTED_ORDER

        self.slot_y_positions = [
            LAYOUT["top_row_y"] - row_index * LAYOUT["row_step"] for row_index in range(N_ROWS)
        ]

        self.active_note = None

        self.build_static_layout()

        self.play_setup_intro()
        self.play_sort_on_phenotype()

        self.mark_video_split("part_02_causes_to_covariance")

        self.play_causes_follow_sorting()
        self.play_covariance_expansion()

        self.mark_video_split("part_03_genetic_component")

        self.play_genetic_covariance_substitution()

    # -----------------------------------------------------------------------
    # General helper methods
    # -----------------------------------------------------------------------
    def mark_video_split(self, section_name):
        """Start a new output section if rendering with --save_sections."""
        if ENABLE_VIDEO_SPLITS:
            self.next_section(section_name)

    def color_equation(self, equation):
        """
        Apply the same color language to equations throughout the scene.

        Repeating the same color mapping makes the lecture easier to follow:
        y always means phenotype, g always means genetic value, and so on.
        """
        equation.set_color_by_tex("y_m", COLORS["phenotype"])
        equation.set_color_by_tex("y_p", COLORS["phenotype"])
        equation.set_color_by_tex("y_i", COLORS["phenotype"])
        equation.set_color_by_tex("y", COLORS["phenotype"])
        equation.set_color_by_tex("g_m", COLORS["genetic"])
        equation.set_color_by_tex("g_p", COLORS["genetic"])
        equation.set_color_by_tex("g_i", COLORS["genetic"])
        equation.set_color_by_tex("g", COLORS["genetic"])
        equation.set_color_by_tex("e_m", COLORS["environment"])
        equation.set_color_by_tex("e_p", COLORS["environment"])
        equation.set_color_by_tex("e_i", COLORS["environment"])
        equation.set_color_by_tex("e", COLORS["environment"])
        equation.set_color_by_tex(r"x_{ij}", COLORS["support"])
        equation.set_color_by_tex(r"x_{mj}", COLORS["support"])
        equation.set_color_by_tex(r"x_{pk}", COLORS["support"])
        equation.set_color_by_tex(r"\beta_j", COLORS["support"])
        equation.set_color_by_tex(r"\beta_k", COLORS["support"])
        return equation

    def make_right_panel_note(self, *lines, center=None):
        """Create the fixed teaching area used throughout the scene."""
        note_lines = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        if note_lines.width > LAYOUT["right_panel_max_width"]:
            note_lines.scale_to_fit_width(LAYOUT["right_panel_max_width"])

        background = BackgroundRectangle(
            note_lines,
            buff=0.22,
            fill_opacity=0.12,
            stroke_opacity=0.0,
        )
        panel = VGroup(background, note_lines)
        panel.move_to(LAYOUT["right_panel_center"] if center is None else center)
        return panel

    def swap_note(self, new_note):
        """Replace the current equation block while keeping the left side stable."""
        if self.active_note is None:
            self.play(FadeIn(new_note, shift=0.10 * UP), run_time=0.6)
        else:
            self.play(
                FadeOut(self.active_note, shift=0.10 * DOWN),
                FadeIn(new_note, shift=0.10 * UP),
                run_time=0.6,
            )
        self.active_note = new_note

    def make_value_cell(self, value, box_color, fill_opacity, font_size=None):
        """
        Build one displayed scalar value.

        The values are intentionally plain numbers rather than boxed entries.
        A small invisible anchor keeps later layout and highlighting helpers
        simple while leaving the visible display uncluttered.
        """
        entry = MathTex(
            format_decimal(value),
            font_size=LAYOUT["cell_font_size"] if font_size is None else font_size,
        )
        entry.set_color(box_color)

        anchor = RoundedRectangle(
            corner_radius=0.02,
            width=LAYOUT["cell_width"],
            height=LAYOUT["cell_height"],
            stroke_opacity=0.0,
            fill_opacity=0.0,
        )
        entry.move_to(anchor.get_center())

        group = VGroup(anchor, entry)
        return {"box": anchor, "entry": entry, "group": group, "value": value}

    def build_person_column_triplet(self, person_data, side_key):
        """
        Build the three displayed values for one person.

        The visual order differs by side so the final layout reads as:
            g_m | e_m | y_m || y_p | g_p | e_p
        """
        cell_map = {
            "g": self.make_value_cell(person_data["g"], COLORS["genetic"], fill_opacity=0.0),
            "e": self.make_value_cell(person_data["e"], COLORS["environment"], fill_opacity=0.0),
            "y": self.make_value_cell(person_data["y"], COLORS["phenotype"], fill_opacity=0.0),
        }

        display_order = ["g", "e", "y"] if side_key == "m" else ["y", "g", "e"]
        row_group = VGroup(*[cell_map[key]["group"] for key in display_order]).arrange(
            RIGHT,
            buff=LAYOUT["cell_gap"],
        )

        # Keep g and e present from the start, but visually secondary until the
        # scene explicitly turns to the causes of phenotype.
        component_group = VGroup(cell_map["g"]["group"], cell_map["e"]["group"])
        component_group.set_opacity(LAYOUT["component_muted_opacity"])

        return {
            "data": person_data,
            "side": side_key,
            "cells": cell_map,
            "component_group": component_group,
            "group": row_group,
        }

    def position_column_triplet(self, row_bundle, center_x, y_coordinate):
        """Place one three-number row bundle at its current slot."""
        row_bundle["group"].move_to(np.array([center_x, y_coordinate, 0.0]))

    def make_row_band(self, target_group, color):
        """
        Build a soft horizontal band around a group of rows.

        The band is used instead of many arrows because a grouped highlight is
        much easier to read once we have 16 rows on screen.
        """
        return SurroundingRectangle(
            target_group,
            color=color,
            buff=LAYOUT["band_buff"],
            stroke_width=2.2,
            fill_color=color,
            fill_opacity=0.08,
        )

    def build_headers(self):
        """Create the six column headers after the first rows are positioned."""
        sample_m_row = self.maternal_rows[0]
        sample_p_row = self.paternal_rows[0]

        header_specs = {
            "g_m": (sample_m_row["cells"]["g"]["entry"].get_center()[0], COLORS["genetic"]),
            "e_m": (sample_m_row["cells"]["e"]["entry"].get_center()[0], COLORS["environment"]),
            "y_m": (sample_m_row["cells"]["y"]["entry"].get_center()[0], COLORS["phenotype"]),
            "y_p": (sample_p_row["cells"]["y"]["entry"].get_center()[0], COLORS["phenotype"]),
            "g_p": (sample_p_row["cells"]["g"]["entry"].get_center()[0], COLORS["genetic"]),
            "e_p": (sample_p_row["cells"]["e"]["entry"].get_center()[0], COLORS["environment"]),
        }

        headers = {}
        for tex_label, (x_coordinate, color) in header_specs.items():
            header = MathTex(tex_label, font_size=LAYOUT["header_font_size"])
            header.set_color(color)
            header.move_to(np.array([x_coordinate, LAYOUT["header_y"], 0.0]))
            headers[tex_label] = header

        return headers

    def side_rows_in_order(self, row_list, order):
        """Return the row bundles in the requested order."""
        return [row_list[index] for index in order]

    def get_sorted_rows(self, row_list):
        """Return rows sorted by phenotype y from high to low."""
        return sorted(row_list, key=lambda row: row["data"]["y"], reverse=True)

    def get_column_group(self, row_list, header_key, variable_key):
        """Return one full column group including header and all cell entries."""
        return VGroup(
            self.headers[header_key],
            *[row["cells"][variable_key]["group"] for row in row_list],
        )

    def build_static_layout(self):
        """Build the reusable left-side objects and their initial positions."""
        self.maternal_rows = [
            self.build_person_column_triplet(person_data, "m")
            for person_data in self.maternal_people
        ]
        self.paternal_rows = [
            self.build_person_column_triplet(person_data, "p")
            for person_data in self.paternal_people
        ]

        maternal_display_rows = self.side_rows_in_order(
            self.maternal_rows,
            self.maternal_unsorted_order,
        )
        paternal_display_rows = self.side_rows_in_order(
            self.paternal_rows,
            self.paternal_unsorted_order,
        )

        for slot_index, row_bundle in enumerate(maternal_display_rows):
            self.position_column_triplet(
                row_bundle,
                LAYOUT["left_triplet_center_x"],
                self.slot_y_positions[slot_index],
            )

        for slot_index, row_bundle in enumerate(paternal_display_rows):
            self.position_column_triplet(
                row_bundle,
                LAYOUT["right_triplet_center_x"],
                self.slot_y_positions[slot_index],
            )

        self.maternal_rows_sorted = self.get_sorted_rows(self.maternal_rows)
        self.paternal_rows_sorted = self.get_sorted_rows(self.paternal_rows)

        for slot_index, row_bundle in enumerate(self.maternal_rows_sorted):
            row_bundle["sorted_center"] = np.array(
                [LAYOUT["left_triplet_center_x"], self.slot_y_positions[slot_index], 0.0]
            )

        for slot_index, row_bundle in enumerate(self.paternal_rows_sorted):
            row_bundle["sorted_center"] = np.array(
                [LAYOUT["right_triplet_center_x"], self.slot_y_positions[slot_index], 0.0]
            )

        self.headers = self.build_headers()
        self.headers_group = VGroup(*self.headers.values())
        self.maternal_group = VGroup(*[row["group"] for row in self.maternal_rows])
        self.paternal_group = VGroup(*[row["group"] for row in self.paternal_rows])

    # -----------------------------------------------------------------------
    # Section 1: introduce the phenotype decomposition and the sorting target
    # -----------------------------------------------------------------------
    def play_setup_intro(self):
        self.wait(TIMING["short_pause"] * 0.6)

        intro_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"y_i=g_i+e_i", font_size=38)),
            self.color_equation(MathTex(r"g_i=\sum_j \beta_j x_{ij}", font_size=34)),
        )

        self.play(FadeIn(self.headers_group, shift=0.12 * UP), run_time=0.7)
        self.play(
            LaggedStart(
                *[FadeIn(row["group"], shift=0.08 * RIGHT) for row in self.maternal_rows],
                lag_ratio=0.015,
            ),
            LaggedStart(
                *[FadeIn(row["group"], shift=0.08 * RIGHT) for row in self.paternal_rows],
                lag_ratio=0.015,
            ),
            run_time=1.6,
        )
        self.swap_note(intro_note)
        self.wait(TIMING["medium_pause"])

        y_focus = VGroup(
            SurroundingRectangle(
                self.get_column_group(self.maternal_rows, "y_m", "y"),
                color=COLORS["highlight"],
                buff=0.08,
                stroke_width=2.4,
            ),
            SurroundingRectangle(
                self.get_column_group(self.paternal_rows, "y_p", "y"),
                color=COLORS["highlight"],
                buff=0.08,
                stroke_width=2.4,
            ),
        )
        self.play(Create(y_focus), run_time=0.7)
        self.wait(TIMING["short_pause"])
        self.play(FadeOut(y_focus), run_time=0.4)

    # -----------------------------------------------------------------------
    # Section 2: sorting partners on phenotype
    # -----------------------------------------------------------------------
    def play_sort_on_phenotype(self):
        move_animations = []
        for row_bundle in self.maternal_rows:
            move_animations.append(row_bundle["group"].animate.move_to(row_bundle["sorted_center"]))
        for row_bundle in self.paternal_rows:
            move_animations.append(row_bundle["group"].animate.move_to(row_bundle["sorted_center"]))

        self.play(
            LaggedStart(*move_animations, lag_ratio=0.02),
            run_time=TIMING["sorting"],
        )

        y_band_targets = [
            VGroup(
                *[row["cells"]["y"]["group"] for row in self.maternal_rows_sorted[0:4]],
                *[row["cells"]["y"]["group"] for row in self.paternal_rows_sorted[0:4]],
            ),
            VGroup(
                *[row["cells"]["y"]["group"] for row in self.maternal_rows_sorted[6:10]],
                *[row["cells"]["y"]["group"] for row in self.paternal_rows_sorted[6:10]],
            ),
            VGroup(
                *[row["cells"]["y"]["group"] for row in self.maternal_rows_sorted[12:16]],
                *[row["cells"]["y"]["group"] for row in self.paternal_rows_sorted[12:16]],
            ),
        ]

        self.y_rank_bands = VGroup(
            self.make_row_band(y_band_targets[0], COLORS["band_high"]),
            self.make_row_band(y_band_targets[1], COLORS["band_mid"]),
            self.make_row_band(y_band_targets[2], COLORS["band_low"]),
        )

        self.play(Create(self.y_rank_bands), run_time=0.8)
        self.wait(TIMING["medium_pause"])

    # -----------------------------------------------------------------------
    # Section 3: the causes move with the sorted people
    # -----------------------------------------------------------------------
    def play_causes_follow_sorting(self):
        full_row_targets = [
            VGroup(
                *[row["group"] for row in self.maternal_rows_sorted[0:4]],
                *[row["group"] for row in self.paternal_rows_sorted[0:4]],
            ),
            VGroup(
                *[row["group"] for row in self.maternal_rows_sorted[6:10]],
                *[row["group"] for row in self.paternal_rows_sorted[6:10]],
            ),
            VGroup(
                *[row["group"] for row in self.maternal_rows_sorted[12:16]],
                *[row["group"] for row in self.paternal_rows_sorted[12:16]],
            ),
        ]

        full_row_bands = VGroup(
            self.make_row_band(full_row_targets[0], COLORS["band_high"]),
            self.make_row_band(full_row_targets[1], COLORS["band_mid"]),
            self.make_row_band(full_row_targets[2], COLORS["band_low"]),
        )

        self.play(
            *[
                row["component_group"].animate.set_opacity(1.0)
                for row in self.maternal_rows + self.paternal_rows
            ],
            run_time=0.9,
        )
        self.play(
            *[
                Transform(old_band, new_band)
                for old_band, new_band in zip(self.y_rank_bands, full_row_bands)
            ],
            run_time=0.8,
        )
        self.wait(TIMING["medium_pause"])
        self.play(FadeOut(full_row_bands), run_time=0.35)

    # -----------------------------------------------------------------------
    # Section 4: expand the covariance using the covariance-of-sums law
    # -----------------------------------------------------------------------
    def play_covariance_expansion(self):
        self.y_objects = VGroup(
            self.headers["y_m"],
            self.headers["y_p"],
            *[row["cells"]["y"]["group"] for row in self.maternal_rows_sorted],
            *[row["cells"]["y"]["group"] for row in self.paternal_rows_sorted],
        )

        g_m_column = self.get_column_group(self.maternal_rows_sorted, "g_m", "g")
        e_m_column = self.get_column_group(self.maternal_rows_sorted, "e_m", "e")
        g_p_column = self.get_column_group(self.paternal_rows_sorted, "g_p", "g")
        e_p_column = self.get_column_group(self.paternal_rows_sorted, "e_p", "e")

        self.g_visuals = VGroup(self.headers["g_m"], self.headers["g_p"], g_m_column, g_p_column)
        self.e_visuals = VGroup(self.headers["e_m"], self.headers["e_p"], e_m_column, e_p_column)

        self.play(
            FadeOut(self.y_objects),
            VGroup(self.g_visuals, self.e_visuals).animate.set_opacity(0.28),
            run_time=0.6,
        )

        covariance_start = self.make_right_panel_note(
            self.color_equation(MathTex(r"\mathrm{Cov}(y_m,y_p)", font_size=40)),
            center=LAYOUT["equation_panel_center"],
        )
        self.swap_note(covariance_start)
        self.wait(TIMING["short_pause"])

        covariance_middle = self.make_right_panel_note(
            self.color_equation(MathTex(r"\mathrm{Cov}(y_m,y_p)", font_size=36)),
            self.color_equation(
                MathTex(
                    r"=\mathrm{Cov}(g_m+e_m,\ g_p+e_p)",
                    font_size=32,
                )
            ),
            center=LAYOUT["equation_panel_center"],
        )
        self.swap_note(covariance_middle)
        self.wait(TIMING["short_pause"])

        expansion_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"\mathrm{Cov}(y_m,y_p)", font_size=34)),
            self.color_equation(
                MathTex(
                    r"=\mathrm{Cov}(g_m+e_m,\ g_p+e_p)",
                    font_size=30,
                )
            ),
            self.color_equation(MathTex(r"=\mathrm{Cov}(g_m,g_p)", font_size=28)),
            self.color_equation(MathTex(r"+\mathrm{Cov}(e_m,e_p)", font_size=28)),
            self.color_equation(MathTex(r"+\mathrm{Cov}(g_m,e_p)", font_size=28)),
            self.color_equation(MathTex(r"+\mathrm{Cov}(e_m,g_p)", font_size=28)),
            center=LAYOUT["equation_panel_center"],
        )
        self.swap_note(expansion_note)
        self.wait(TIMING["medium_pause"])

        lines = expansion_note[1]
        highlighted_term = lines[2]
        faded_terms = VGroup(lines[3], lines[4], lines[5])

        self.g_pair_highlight = VGroup(
            SurroundingRectangle(
                g_m_column,
                color=COLORS["genetic"],
                buff=0.08,
                stroke_width=2.5,
            ),
            SurroundingRectangle(
                g_p_column,
                color=COLORS["genetic"],
                buff=0.08,
                stroke_width=2.5,
            ),
        )

        self.play(
            faded_terms.animate.set_opacity(0.14),
            highlighted_term.animate.scale(1.05),
            self.g_visuals.animate.set_opacity(0.90),
            self.e_visuals.animate.set_opacity(0.08),
            Create(self.g_pair_highlight),
            run_time=0.8,
        )
        self.wait(TIMING["medium_pause"])

    # -----------------------------------------------------------------------
    # Section 5: focus on the genetic component and substitute the SNP sum
    # -----------------------------------------------------------------------
    def play_genetic_covariance_substitution(self):
        component_numbers = VGroup(
            *[row["component_group"] for row in self.maternal_rows_sorted],
            *[row["component_group"] for row in self.paternal_rows_sorted],
        )

        component_headers = VGroup(
            self.headers["g_m"],
            self.headers["e_m"],
            self.headers["g_p"],
            self.headers["e_p"],
        )

        self.play(
            component_numbers.animate.set_opacity(0.12),
            component_headers.animate.set_opacity(0.12),
            self.g_pair_highlight.animate.set_opacity(0.25),
            run_time=0.5,
        )

        substitution_note = self.make_right_panel_note(
            self.color_equation(MathTex(r"g_i=\sum_j \beta_j x_{ij}", font_size=30)),
            self.color_equation(
                MathTex(
                    r"\mathrm{Cov}(g_m,g_p)=\mathrm{Cov}\!\left(\sum_j \beta_j x_{mj},\ \sum_k \beta_k x_{pk}\right)",
                    font_size=23,
                )
            ),
            center=LAYOUT["equation_panel_center"] + np.array([0.20, 0.0, 0.0]),
        )
        self.swap_note(substitution_note)
        self.wait(TIMING["long_pause"])


