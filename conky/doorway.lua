-- Doorway rice — rounded translucent card behind the conky text.
require 'cairo'
pcall(require, 'cairo_xlib')

local S = tonumber(os.getenv('DOORWAY_S') or '2')

local function rounded(cr, x, y, w, h, r)
  cairo_new_sub_path(cr)
  cairo_arc(cr, x + w - r, y + r, r, -math.pi / 2, 0)
  cairo_arc(cr, x + w - r, y + h - r, r, 0, math.pi / 2)
  cairo_arc(cr, x + r, y + h - r, r, math.pi / 2, math.pi)
  cairo_arc(cr, x + r, y + r, r, math.pi, 3 * math.pi / 2)
  cairo_close_path(cr)
end

function conky_card()
  if conky_window == nil then return end
  local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable,
    conky_window.visual, conky_window.width, conky_window.height)
  local cr = cairo_create(cs)
  local w, h = conky_window.width, conky_window.height
  rounded(cr, 0.5, 0.5, w - 1, h - 1, 14 * S)
  cairo_set_source_rgba(cr, 11 / 255, 29 / 255, 34 / 255, 0.86)   -- base #0b1d22
  cairo_fill_preserve(cr)
  cairo_set_line_width(cr, 1 * S)
  cairo_set_source_rgba(cr, 44 / 255, 74 / 255, 80 / 255, 1)      -- line #2c4a50
  cairo_stroke(cr)
  cairo_destroy(cr)
  cairo_surface_destroy(cs)
end
