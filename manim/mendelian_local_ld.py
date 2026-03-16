"""
Manim scene: Mendelian chunk inheritance and local linkage disequilibrium.

This scene intentionally mirrors the visual language in
`mendelian_inheritance_v2.py` so it feels familiar in the same lecture.

Quick render:
    py -m manim -pql manim/mendelian_local_ld.py MendelianLocalLDScene

Higher quality:
    py -m manim --format=mp4 --fps 30 -r 1280,720 \
        manim/mendelian_local_ld.py MendelianLocalLDScene
"""

from manim import *
import numpy as np


# ---------------------------------------------------------------------------
# Top-level configuration
# ---------------------------------------------------------------------------
PARENT_HAPLOTYPE_1 = [1, 1, 0, 0, 1, 1, 0, 0]
PARENT_HAPLOTYPE_2 = [0, 0, 1, 1, 0, 0, 1, 1]

# Single crossover after locus 4 (between loci 4 and 5).
# 0 = inherit from haplotype 1, 1 = inherit from haplotype 2.
TRANSMISSION_PATTERN = [0, 0, 0, 0, 1, 1, 1, 1]
CROSSOVER_AFTER_LOCUS = 4

TIMING = {
    "short_pause": 1.0,
    "medium_pause": 1.6,
    "long_pause": 2.3,
    "chunk_animation": 0.8,
}

COLORS = {
    "haplotype_1": BLUE_E,
    "haplotype_2": TEAL_E,
    "gamete": GREEN_E,
    "segregation": PURPLE_B,
    "highlight": YELLOW,
    "contrast": RED_C,
    "assumption": GREY_B,
}

LAYOUT = {
    "cells_center_x": -1.7,
    "label_buffer": 0.45,
    "cell_gap": 0.14,
    "cell_width": 0.74,
    "cell_height": 0.56,
    "locus_label_y_offset": 0.24,
    "right_panel_center": np.array([3.9, 0.85, 0.0]),
}

ENABLE_VIDEO_SPLITS = True


def compute_transmitted_alleles(haplotype_1, haplotype_2, transmission_pattern):
    """Return transmitted haplotype alleles under a fixed source pattern."""
    transmitted = []
    for upper, lower, chosen_haplotype in zip(
        haplotype_1,
        haplotype_2,
        transmission_pattern,
    ):
        transmitted.append(upper if chosen_haplotype == 0 else lower)
    return transmitted


class MendelianLocalLDScene(Scene):
    """
    Show that nearby SNPs are often inherited together in chunks, inducing local LD.
    """

    def construct(self):
        self.haplotype_1 = PARENT_HAPLOTYPE_1
        self.haplotype_2 = PARENT_HAPLOTYPE_2
        self.transmission_pattern = TRANSMISSION_PATTERN
        self.transmitted_alleles = compute_transmitted_alleles(
            self.haplotype_1,
            self.haplotype_2,
            self.transmission_pattern,
        )
        self.active_note = None

        self.build_static_layout()

        self.play_parent_intro()
        self.play_crossover_marker()
        self.play_chunk_transfer()

        self.mark_video_split("part_02_local_ld_takeaway")

        self.play_local_ld_takeaway()

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def mark_video_split(self, section_name):
        if ENABLE_VIDEO_SPLITS:
            self.next_section(section_name)

    def make_value_cell(
        self,
        value,
        box_color,
        fill_opacity=0.18,
        font_size=30,
    ):
        box = RoundedRectangle(
            corner_radius=0.08,
            width=LAYOUT["cell_width"],
            height=LAYOUT["cell_height"],
            stroke_color=box_color,
            stroke_width=2.0,
            fill_color=box_color,
            fill_opacity=fill_opacity,
        )

        if value is not None:
            entry = MathTex(str(value), font_size=font_size)
            entry.move_to(box.get_center())
        else:
            entry = VectorizedPoint(box.get_center())

        group = VGroup(box, entry)
        return {"box": box, "entry": entry, "group": group, "value": value}

    def build_row(self, values, label_tex, box_color):
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
        row["cells_group"].move_to(np.array([LAYOUT["cells_center_x"], y_coordinate, 0.0]))
        row["label"].next_to(row["cells_group"], LEFT, buff=LAYOUT["label_buffer"])
        row["group"] = VGroup(row["label"], row["cells_group"])

    def build_locus_labels(self, reference_row):
        labels = VGroup()
        for locus_index, cell in enumerate(reference_row["cells"], start=1):
            label = MathTex(fr"j={locus_index}", font_size=23)
            label.next_to(cell["box"], UP, buff=LAYOUT["locus_label_y_offset"])
            labels.add(label)
        return labels

    def make_right_panel_note(self, *lines, center=None):
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

    def swap_note(self, new_note):
        if self.active_note is None:
            self.play(FadeIn(new_note, shift=0.08 * UP), run_time=0.55)
        else:
            self.play(
                FadeOut(self.active_note, shift=0.08 * DOWN),
                FadeIn(new_note, shift=0.08 * UP),
                run_time=0.55,
            )
        self.active_note = new_note

    def color_equation(self, equation):
        equation.set_color_by_tex(r"\mathrm{Cov}", COLORS["segregation"])
        equation.set_color_by_tex(r"X_j", COLORS["gamete"])
        equation.set_color_by_tex(r"X_k", COLORS["gamete"])
        equation.set_color_by_tex(r"\text{nearby}", COLORS["highlight"])
        equation.set_color_by_tex(r"\text{local LD}", COLORS["segregation"])
        return equation

    def build_static_layout(self):
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
        self.gamete_row = self.build_row(
            [None] * len(self.haplotype_1),
            r"\text{haplotype }z_{j}",
            COLORS["gamete"],
        )

        self.position_row(self.haplotype_row_1, 1.45)
        self.position_row(self.haplotype_row_2, 0.55)
        self.position_row(self.gamete_row, -1.25)
        self.gamete_row["group"].set_opacity(0.0)

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

        left_box = self.haplotype_row_1["cells"][CROSSOVER_AFTER_LOCUS - 1]["box"]
        right_box = self.haplotype_row_1["cells"][CROSSOVER_AFTER_LOCUS]["box"]
        boundary_x = 0.5 * (left_box.get_right()[0] + right_box.get_left()[0])
        top_y = self.haplotype_row_1["cells"][0]["box"].get_top()[1] + 0.22
        bottom_y = self.haplotype_row_2["cells"][0]["box"].get_bottom()[1] - 0.22

        self.crossover_line = DashedLine(
            start=np.array([boundary_x, top_y, 0.0]),
            end=np.array([boundary_x, bottom_y, 0.0]),
            color=COLORS["highlight"],
            dash_length=0.10,
            dashed_ratio=0.60,
            stroke_width=3.0,
        )

        self.crossover_label = Text(
            "crossover point",
            font_size=22,
            color=COLORS["highlight"],
        )
        self.crossover_label.next_to(self.crossover_line, UP, buff=0.16)

    # -----------------------------------------------------------------------
    # Sections
    # -----------------------------------------------------------------------
    def play_parent_intro(self):
        self.wait(TIMING["short_pause"] * 0.5)

        self.play(
            LaggedStart(*[Write(label) for label in self.locus_labels], lag_ratio=0.07),
            run_time=1.1,
        )
        self.play(
            FadeIn(self.haplotype_row_1["group"], shift=0.12 * RIGHT),
            FadeIn(self.haplotype_row_2["group"], shift=0.12 * RIGHT),
            run_time=0.95,
        )

        self.play(
            Create(self.haplotype_brace),
            FadeIn(self.haplotype_brace_label, shift=0.10 * RIGHT),
            run_time=0.8,
        )

        intro_note = self.make_right_panel_note(
            Text("Mendelian inheritance in meiosis", font_size=28),
            Text("Chromosome segments are passed to the gamete", font_size=24),
        )
        self.swap_note(intro_note)
        self.wait(TIMING["short_pause"])
        self.play(FadeOut(self.haplotype_brace), FadeOut(self.haplotype_brace_label), run_time=0.55)

    def play_crossover_marker(self):
        crossover_note = self.make_right_panel_note(
            Text("Single crossover between loci 4 and 5", font_size=26),
            Text("Inheritance switches source haplotype at the breakpoint", font_size=22),
        )
        self.swap_note(crossover_note)
        self.play(
            Create(self.crossover_line),
            FadeIn(self.crossover_label, shift=0.1 * UP),
            run_time=0.8,
        )
        self.wait(TIMING["short_pause"] * 0.7)

    def chunk_cells(self, row, start_idx, end_idx):
        return VGroup(*[row["cells"][i]["group"] for i in range(start_idx, end_idx + 1)])

    def animate_chunk_transfer(self, start_idx, end_idx, source_row):
        source_chunk = self.chunk_cells(source_row, start_idx, end_idx)
        target_chunk = self.chunk_cells(self.gamete_row, start_idx, end_idx)

        source_highlight = SurroundingRectangle(
            source_chunk,
            color=COLORS["gamete"],
            buff=0.08,
            corner_radius=0.10,
        )
        target_highlight = SurroundingRectangle(
            target_chunk,
            color=COLORS["gamete"],
            buff=0.08,
            corner_radius=0.10,
        )

        transfer_arrow = Arrow(
            source_highlight.get_bottom(),
            target_highlight.get_top(),
            buff=0.08,
            stroke_width=4,
            color=COLORS["gamete"],
            max_tip_length_to_length_ratio=0.16,
        )

        target_entries = []
        transforms = []
        for locus_index in range(start_idx, end_idx + 1):
            source_cell = source_row["cells"][locus_index]
            target_cell = self.gamete_row["cells"][locus_index]
            new_entry = MathTex(str(self.transmitted_alleles[locus_index]), font_size=30)
            new_entry.move_to(target_cell["box"].get_center())
            target_entries.append((target_cell, new_entry))
            transforms.append(TransformFromCopy(source_cell["entry"], new_entry))

        self.play(Create(source_highlight), Create(target_highlight), run_time=0.32)
        self.play(GrowArrow(transfer_arrow), run_time=0.20)
        self.play(*transforms, run_time=TIMING["chunk_animation"])

        for target_cell, new_entry in target_entries:
            target_cell["group"].remove(target_cell["entry"])
            target_cell["entry"] = new_entry
            target_cell["group"].add(new_entry)

        self.play(
            FadeOut(source_highlight),
            FadeOut(target_highlight),
            FadeOut(transfer_arrow),
            run_time=0.18,
        )

    def play_chunk_transfer(self):
        chunk_note = self.make_right_panel_note(
            Text("Gamete receives contiguous SNP chunks", font_size=27),
            Text("Not independent locus-by-locus draws", font_size=23),
        )
        self.swap_note(chunk_note)
        self.play(FadeIn(self.gamete_row["group"], shift=0.1 * RIGHT), run_time=0.55)

        # Left chunk (loci 1-4) from haplotype 1.
        self.animate_chunk_transfer(0, 3, self.haplotype_row_1)

        # Right chunk (loci 5-8) from haplotype 2.
        self.animate_chunk_transfer(4, 7, self.haplotype_row_2)
        self.wait(TIMING["short_pause"] * 0.65)

        self.gamete_brace = Brace(self.gamete_row["cells_group"], DOWN, buff=0.16)
        self.gamete_brace_label = self.gamete_brace.get_text(
            "inherited in chunks",
            buff=0.10,
        )
        self.gamete_brace_label.scale(0.5)
        self.gamete_brace_label.set_color(COLORS["gamete"])
        self.play(
            Create(self.gamete_brace),
            FadeIn(self.gamete_brace_label, shift=0.08 * DOWN),
            run_time=0.55,
        )
        self.wait(TIMING["short_pause"] * 0.6)

    def play_local_ld_takeaway(self):
        nearby_indices = [1, 2]  # j=2,3 (same inherited chunk)
        far_indices = [2, 5]     # j=3,6 (across the crossover boundary)

        nearby_rect_parent = SurroundingRectangle(
            VGroup(*[self.haplotype_row_1["cells"][i]["box"] for i in nearby_indices]),
            color=COLORS["highlight"],
            buff=0.08,
        )
        nearby_rect_gamete = SurroundingRectangle(
            VGroup(*[self.gamete_row["cells"][i]["box"] for i in nearby_indices]),
            color=COLORS["highlight"],
            buff=0.08,
        )
        nearby_note = self.make_right_panel_note(
            Text("Nearby SNPs (j=2,3) are co-inherited", font_size=26),
            Text("They move together inside one inherited chunk", font_size=22),
        )
        self.swap_note(nearby_note)
        self.play(
            Create(nearby_rect_parent),
            Create(nearby_rect_gamete),
            run_time=0.55,
        )
        self.wait(TIMING["medium_pause"] * 0.65)

        far_left_parent = SurroundingRectangle(
            self.haplotype_row_1["cells"][far_indices[0]]["box"],
            color=COLORS["contrast"],
            buff=0.07,
        )
        far_right_parent = SurroundingRectangle(
            self.haplotype_row_2["cells"][far_indices[1]]["box"],
            color=COLORS["contrast"],
            buff=0.07,
        )
        far_left_gamete = SurroundingRectangle(
            self.gamete_row["cells"][far_indices[0]]["box"],
            color=COLORS["contrast"],
            buff=0.07,
        )
        far_right_gamete = SurroundingRectangle(
            self.gamete_row["cells"][far_indices[1]]["box"],
            color=COLORS["contrast"],
            buff=0.07,
        )
        far_note = self.make_right_panel_note(
            Text("More distant SNPs can be split by crossover", font_size=25),
            Text("Across the breakpoint, co-inheritance is weaker", font_size=22),
        )
        self.swap_note(far_note)
        self.play(
            FadeOut(nearby_rect_parent),
            FadeOut(nearby_rect_gamete),
            run_time=0.28,
        )
        self.play(
            Create(far_left_parent),
            Create(far_right_parent),
            Create(far_left_gamete),
            Create(far_right_gamete),
            Indicate(self.crossover_line, color=COLORS["contrast"], scale_factor=1.02),
            run_time=0.72,
        )
        self.wait(TIMING["medium_pause"] * 0.6)

        final_equation = self.color_equation(
            MathTex(
                r"\text{nearby }j,k \Rightarrow \mathrm{Cov}(X_j, X_k)\neq 0",
                font_size=35,
            )
        )
        bridge_line = self.color_equation(
            MathTex(
                r"\text{physical proximity}\rightarrow\text{linkage}\rightarrow\text{local LD}",
                font_size=30,
            )
        )
        final_note = self.make_right_panel_note(final_equation, bridge_line)

        self.play(
            FadeOut(far_left_parent),
            FadeOut(far_right_parent),
            FadeOut(far_left_gamete),
            FadeOut(far_right_gamete),
            run_time=0.28,
        )
        self.swap_note(final_note)
        self.wait(TIMING["long_pause"])

        if self.active_note is not None:
            self.play(FadeOut(self.active_note), run_time=0.4)
