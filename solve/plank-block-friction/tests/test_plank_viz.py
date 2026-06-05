"""Smoke tests for dual-panel visualization."""

from paths import ami_dir

from plank_block_friction.constants import CASE_ID
from plank_block_friction.presets import sim_config_for_preset
from plank_block_friction.simulation import run_simulation
from plank_block_friction.constants import VIEW_X_SPAN
from plank_block_friction.contact import is_block_on_plank
from plank_block_friction.scene_layout import build_scene_layout
from plank_block_friction.viz import (
    block_anchor_x,
    block_view_xlim,
    export_dual_frame_png,
    friction_opposes_v_rel,
    lab_to_block_screen_x,
    lab_view_xlim,
    portrait_aspect_ratio,
    render_dual_frame,
)


def test_portrait_aspect_ratio():
    assert abs(portrait_aspect_ratio() - 16 / 9) < 0.01


def test_render_dual_frame_does_not_raise():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.15)
    fig = render_dual_frame(traj.samples[50])
    assert fig is not None
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_friction_opposes_v_rel_during_sliding():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.5)
    sliding = [s for s in traj.samples if s.block_plank_kinetic and s.t > 0.01]
    assert sliding
    assert all(friction_opposes_v_rel(s) for s in sliding)


def test_ground_panel_uses_fixed_lab_window():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.5)
    early = traj.samples[10]
    late = traj.samples[500]
    fig1 = render_dual_frame(early)
    fig2 = render_dual_frame(late)
    ax1, ax2 = fig1.axes[0], fig2.axes[0]
    assert ax1.get_xlim() == ax2.get_xlim() == lab_view_xlim()
    import matplotlib.pyplot as plt

    plt.close(fig1)
    plt.close(fig2)


def test_block_panel_pins_block_and_scrolls_ground():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.4)
    s0 = traj.samples[0]
    s1 = traj.samples[200]
    assert s1.x_block > s0.x_block
    fig0 = render_dual_frame(s0)
    fig1 = render_dual_frame(s1)
    ax0, ax1 = fig0.axes[1], fig1.axes[1]
    assert ax0.get_xlim() == ax1.get_xlim() == block_view_xlim()
    # Block rectangle center stays at anchor in lower panel.
    assert lab_to_block_screen_x(s0.x_block, s0.x_block) == block_anchor_x()
    assert lab_to_block_screen_x(s1.x_block, s1.x_block) == block_anchor_x()
    import matplotlib.pyplot as plt

    plt.close(fig0)
    plt.close(fig1)


def test_axes_use_equal_meter_scale():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.05)
    fig = render_dual_frame(traj.samples[0])
    for ax in fig.axes:
        x_span = ax.get_xlim()[1] - ax.get_xlim()[0]
        y_span = ax.get_ylim()[1] - ax.get_ylim()[0]
        assert abs(x_span - y_span) < 1e-6
        assert abs(ax.get_aspect() - 1.0) < 1e-6
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_block_patch_is_square_in_data_coords():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.05)
    fig = render_dual_frame(traj.samples[0])
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


def test_panels_share_horizontal_span():
    assert lab_view_xlim()[1] - lab_view_xlim()[0] == VIEW_X_SPAN
    assert block_view_xlim()[1] - block_view_xlim()[0] == VIEW_X_SPAN


def test_fallen_block_sits_on_ground():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.5)
    fallen = next(
        s
        for s in traj.samples
        if s.t > 0 and not is_block_on_plank(s.x_block, s.x_plank)
    )
    scene = build_scene_layout(fallen)
    assert not scene.on_plank
    assert scene.block_bottom_y == 0.0


def test_export_dual_frame_png_to_ami():
    traj = run_simulation(sim_config_for_preset("preset-1"), 0.1)
    out = ami_dir(CASE_ID) / "_test_frame.png"
    export_dual_frame_png(traj.samples[10], out)
    assert out.is_file()
    assert out.stat().st_size > 500
    out.unlink(missing_ok=True)
