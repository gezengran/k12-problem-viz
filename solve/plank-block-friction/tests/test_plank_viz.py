"""Smoke tests for single-view ground / block visualization."""

import pytest
from paths import ami_dir

from plank_block_friction.constants import (
    BLOCK_VIEW_X_SPAN,
    CASE_ID,
    FIG_HEIGHT,
    FIG_WIDTH,
    LAB_VIEW_X_SPAN,
    LAB_X_MIN,
    PLANK_LENGTH,
    VIEW_X_SPAN,
)
from plank_block_friction.presets import animation_duration, sim_config_for_preset
from plank_block_friction.simulation import run_simulation
from plank_block_friction.contact import is_block_on_plank
from plank_block_friction.viz import (
    block_anchor_x,
    block_view_xlim,
    export_frame_png,
    figure_aspect_ratio,
    friction_opposes_v_rel,
    lab_to_block_screen_x,
    lab_to_plank_screen_x,
    lab_view_xlim,
    plank_anchor_x,
    plank_view_xlim,
    render_block_frame,
    render_ground_frame,
    render_plank_frame,
)


def test_landscape_aspect_ratio():
    assert abs(figure_aspect_ratio() - 3 / 4) < 0.01


def test_render_single_view_frames_do_not_raise():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.15)
    sample = traj.samples[50]
    fig_g = render_ground_frame(sample)
    fig_b = render_block_frame(sample)
    fig_p = render_plank_frame(sample)
    assert fig_g is not None and fig_b is not None and fig_p is not None
    import matplotlib.pyplot as plt

    plt.close(fig_g)
    plt.close(fig_b)
    plt.close(fig_p)


def test_friction_opposes_v_rel_during_sliding():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.5)
    sliding = [s for s in traj.samples if s.block_plank_kinetic and s.t > 0.01]
    assert sliding
    assert all(friction_opposes_v_rel(s) for s in sliding)


def test_ground_and_block_views_share_same_horizontal_span():
    traj = run_simulation(sim_config_for_preset("preset-2"), 1.0)
    for sample in (traj.samples[0], traj.samples[300], traj.samples[-1]):
        fig_g = render_ground_frame(sample)
        fig_b = render_block_frame(sample)
        left = fig_g.axes[0]
        right = fig_b.axes[0]
        assert left.get_xlim() == (LAB_X_MIN, LAB_X_MIN + LAB_VIEW_X_SPAN)
        assert left.get_xlim() == lab_view_xlim(sample)
        assert right.get_xlim() == block_view_xlim(sample)
        ground_span = left.get_xlim()[1] - left.get_xlim()[0]
        block_span = right.get_xlim()[1] - right.get_xlim()[0]
        assert ground_span == block_span == LAB_VIEW_X_SPAN
        import matplotlib.pyplot as plt

        plt.close(fig_g)
        plt.close(fig_b)


def test_ground_and_block_panels_use_different_reference_maps():
    traj = run_simulation(sim_config_for_preset("preset-2"), 0.4)
    sample = next(s for s in traj.samples if s.t > 0.08)
    fig_g = render_ground_frame(sample)
    fig_b = render_block_frame(sample)
    left, right = fig_g.axes[0], fig_b.axes[0]

    def block_patch_x(ax):
        blocks = [
            p
            for p in ax.patches
            if p.get_facecolor()[0] < 0.5 and p.get_height() > 0.3
        ]
        assert len(blocks) == 1
        return blocks[0].get_x() + blocks[0].get_width() / 2

    left_cx = block_patch_x(left)
    right_cx = block_patch_x(right)
    assert right_cx == pytest.approx(block_anchor_x())
    assert left_cx == pytest.approx(sample.x_block, rel=0.05)
    assert left_cx != pytest.approx(right_cx)
    import matplotlib.pyplot as plt

    plt.close(fig_g)
    plt.close(fig_b)


def test_plank_panel_pins_plank_and_scrolls_ground():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.4)
    s0 = traj.samples[0]
    s1 = traj.samples[200]
    assert s1.x_plank > s0.x_plank
    fig0 = render_plank_frame(s0)
    fig1 = render_plank_frame(s1)
    ax0, ax1 = fig0.axes[0], fig1.axes[0]
    assert ax0.get_xlim() == ax1.get_xlim() == plank_view_xlim()
    plank_left = plank_anchor_x() - PLANK_LENGTH / 2
    assert lab_to_plank_screen_x(s0.x_plank, s0.x_plank) == pytest.approx(plank_left)
    assert lab_to_plank_screen_x(s1.x_plank, s1.x_plank) == pytest.approx(plank_left)
    import matplotlib.pyplot as plt

    plt.close(fig0)
    plt.close(fig1)


def test_block_panel_pins_block_and_scrolls_ground():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.4)
    s0 = traj.samples[0]
    s1 = traj.samples[200]
    assert s1.x_block > s0.x_block
    fig0 = render_block_frame(s0)
    fig1 = render_block_frame(s1)
    ax0, ax1 = fig0.axes[0], fig1.axes[0]
    assert ax0.get_xlim() == ax1.get_xlim() == block_view_xlim()
    assert lab_to_block_screen_x(s0.x_block, s0.x_block) == block_anchor_x()
    assert lab_to_block_screen_x(s1.x_block, s1.x_block) == block_anchor_x()
    import matplotlib.pyplot as plt

    plt.close(fig0)
    plt.close(fig1)


def test_axes_use_equal_meter_scale():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.05)
    for fig in (render_ground_frame(traj.samples[0]), render_block_frame(traj.samples[0])):
        ax = fig.axes[0]
        x_span = ax.get_xlim()[1] - ax.get_xlim()[0]
        y_span = ax.get_ylim()[1] - ax.get_ylim()[0]
        assert abs(x_span / y_span - FIG_WIDTH / FIG_HEIGHT) < 1e-6
        assert abs(ax.get_aspect() - 1.0) < 1e-6
        import matplotlib.pyplot as plt

        plt.close(fig)


def test_block_patch_is_square_in_data_coords():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.05)
    fig = render_ground_frame(traj.samples[0])
    blocks = [
        p
        for ax in fig.axes
        for p in ax.patches
        if p.get_facecolor()[0] < 0.5 and p.get_height() > 0.3
    ]
    assert blocks
    for patch in blocks:
        assert abs(patch.get_width() - patch.get_height()) < 1e-6
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_panel_horizontal_spans():
    assert lab_view_xlim()[1] - lab_view_xlim()[0] == LAB_VIEW_X_SPAN
    assert block_view_xlim()[1] - block_view_xlim()[0] == LAB_VIEW_X_SPAN
    assert BLOCK_VIEW_X_SPAN == LAB_VIEW_X_SPAN
    assert VIEW_X_SPAN == LAB_VIEW_X_SPAN


def test_block_panel_shows_only_rel_vectors_during_sliding():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.3)
    sliding = next(s for s in traj.samples if s.block_plank_kinetic and s.t > 0.05)
    fig = render_block_frame(sliding)
    right = fig.axes[0]
    for text in right.texts:
        label = text.get_text()
        assert label not in (r"$v_{\mathrm{块}}$", r"$v_{\mathrm{板}}$")
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_block_stays_on_plank_during_preset1_animation():
    dur = animation_duration("preset-1")
    traj = run_simulation(sim_config_for_preset("preset-1"), dur)
    assert all(is_block_on_plank(s.x_block, s.x_plank) for s in traj.samples)


def test_export_single_view_png_to_ami():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.1)
    sample = traj.samples[10]
    for view in ("ground", "block", "plank"):
        out = ami_dir(CASE_ID) / f"_test_{view}.png"
        export_frame_png(sample, view, out)
        assert out.is_file()
        assert out.stat().st_size > 500
        out.unlink(missing_ok=True)
