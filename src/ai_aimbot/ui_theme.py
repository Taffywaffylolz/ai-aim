from __future__ import annotations

import imgui


def apply_neon_purple_theme() -> None:
    """Neon purple ImGui style preset."""
    style = imgui.get_style()
    colors = style.colors

    colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.05, 0.02, 0.08, 0.96)
    colors[imgui.COLOR_TITLE_BACKGROUND] = (0.30, 0.05, 0.45, 1.00)
    colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.45, 0.10, 0.75, 1.00)
    colors[imgui.COLOR_FRAME_BACKGROUND] = (0.16, 0.04, 0.25, 0.85)
    colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.28, 0.06, 0.42, 0.95)
    colors[imgui.COLOR_BUTTON] = (0.35, 0.03, 0.64, 0.85)
    colors[imgui.COLOR_BUTTON_HOVERED] = (0.53, 0.10, 0.92, 1.00)
    colors[imgui.COLOR_BUTTON_ACTIVE] = (0.75, 0.18, 1.00, 1.00)
    colors[imgui.COLOR_CHECK_MARK] = (0.85, 0.25, 1.00, 1.00)
    colors[imgui.COLOR_SLIDER_GRAB] = (0.70, 0.20, 1.00, 0.95)
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = (0.88, 0.35, 1.00, 1.00)

    style.window_rounding = 10
    style.frame_rounding = 8
    style.grab_rounding = 8
