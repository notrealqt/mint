// Doorway rice — window gaps (see ~/rice/README.md, #19).
// 1. Panel gap: an invisible strut GAP px taller than each top panel, so maximised and tiled
//    windows start GAP px below it.
// 2. Tile gap: muffin forces tiled windows to fill their tile exactly, so instead each tiled
//    window gets a shader that hides GAP px on any left/top edge facing another tile and
//    rounds its corners by RADIUS (a plain clip can only cut square corners).
// Stage px are 2x (fractional scaling): GAP 8 = 4px, RADIUS 6 = 3px.
const Main = imports.ui.main;
const Meta = imports.gi.Meta;
const St = imports.gi.St;
const GLib = imports.gi.GLib;
const Clutter = imports.gi.Clutter;

const GAP = 8, RADIUS = 6, EFFECT = 'doorway-round';
// p = pixel inside the offscreen texture (same origin as the window actor); rect = visible box.
const SHADER = `
uniform sampler2D tex;
uniform float w, h, x0, y0, x1, y1, r;
void main() {
    vec2 p = cogl_tex_coord_in[0].st * vec2(w, h);
    vec2 d = max(max(vec2(x0, y0) + r - p, p - vec2(x1, y1) + r), 0.0);
    float a = clamp(r + 0.5 - length(d), 0.0, 1.0);
    if (p.x < x0 || p.y < y0 || p.x > x1 || p.y > y1) a = 0.0;
    cogl_color_out = texture2D(tex, cogl_tex_coord_in[0].st) * cogl_color_in * a;
}`;
// a whole number would reach GL as an int uniform; nudge it so GJS sends a double
const f = n => n + 0.0001;
let struts = [], panelIds = [], winIds = new Map(), sigs = [], pending = 0, settle = 0, rebuildId = 0;

// ---- panel gap ----
function clearStruts() {
    struts.forEach(a => { Main.layoutManager.removeChrome(a); a.destroy(); });
    struts = [];
    panelIds.forEach(([actor, id]) => actor.disconnect(id));
    panelIds = [];
}

function rebuild() {
    rebuildId = 0;
    clearStruts();
    for (let panel of Main.panelManager.panels) {
        if (!panel) continue;
        let mon = Main.layoutManager.monitors[panel.monitorIndex];
        if (!mon || panel.actor.y !== mon.y) continue;          // top panels only
        let a = new St.Widget({ reactive: false, x: mon.x, y: mon.y,
                                width: mon.width, height: panel.actor.height + GAP });
        Main.layoutManager.addChrome(a, { affectsStruts: true, affectsInputRegion: false });
        struts.push(a);
        panelIds.push([panel.actor, panel.actor.connect('notify::height', queueRebuild)]);
    }
    return GLib.SOURCE_REMOVE;
}

function queueRebuild() {
    if (!rebuildId) rebuildId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, rebuild);
}

// ---- tile gap ----
function allWindows() {
    return global.get_window_actors().map(a => a.meta_window).filter(w => w);
}

function clip(win) {
    let actor = win.get_compositor_private();
    if (!actor) return;
    let effect = actor.get_effect(EFFECT);
    if (!win.tile_mode || win.get_maximized() === Meta.MaximizeFlags.BOTH) {
        if (effect) actor.remove_effect(effect);
        return;
    }
    if (!effect) {
        effect = new Clutter.ShaderEffect({ shader_type: Clutter.ShaderType.FRAGMENT_SHADER });
        effect.set_shader_source(SHADER);
        actor.add_effect_with_name(EFFECT, effect);
    }
    let fr = win.get_frame_rect(), b = win.get_buffer_rect();   // buffer = actor origin, minus animation
    let area = win.get_work_area_current_monitor();
    let left = fr.x > area.x ? GAP : 0, top = fr.y > area.y ? GAP : 0;
    let [ok, tw, th] = effect.get_target_size();                 // texture is a little bigger than the buffer
    if (!ok) [tw, th] = [b.width, b.height];
    let x0 = fr.x - b.x + left, y0 = fr.y - b.y + top;
    effect.set_uniform_value('w', f(tw));
    effect.set_uniform_value('h', f(th));
    effect.set_uniform_value('x0', f(x0));
    effect.set_uniform_value('y0', f(y0));
    effect.set_uniform_value('x1', f(fr.x - b.x + fr.width));
    effect.set_uniform_value('y1', f(fr.y - b.y + fr.height));
    effect.set_uniform_value('r', f(RADIUS));
}

function clipAll() {
    pending = 0;
    allWindows().forEach(clip);
    if (!settle) settle = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 300, () => {
        settle = 0;
        allWindows().forEach(clip);
        return GLib.SOURCE_REMOVE;
    });
    return GLib.SOURCE_REMOVE;
}

function queueClip() {
    if (!pending) pending = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 30, clipAll);
}

function watch(win) {
    if (winIds.has(win)) return;
    winIds.set(win, ['size-changed', 'position-changed'].map(s => win.connect(s, queueClip)));
    win.connect('unmanaged', () => winIds.delete(win));
}

function init(metadata) {}

function enable() {
    allWindows().forEach(watch);
    sigs.push([global.display, global.display.connect('window-created', (d, w) => { watch(w); queueClip(); })]);
    sigs.push([global.display, global.display.connect('workareas-changed', queueClip)]);
    sigs.push([Main.layoutManager, Main.layoutManager.connect('monitors-changed', queueRebuild)]);
    sigs.push([global.settings, global.settings.connect('changed::panels-enabled', queueRebuild)]);
    sigs.push([global.settings, global.settings.connect('changed::panels-height', queueRebuild)]);
    rebuild();
    clipAll();
}

function disable() {
    sigs.forEach(([obj, id]) => obj.disconnect(id));
    sigs = [];
    winIds.forEach((ids, win) => ids.forEach(id => win.disconnect(id)));
    winIds.clear();
    [pending, settle, rebuildId].forEach(id => { if (id) GLib.source_remove(id); });
    pending = settle = rebuildId = 0;
    clearStruts();
    allWindows().forEach(w => {
        let a = w.get_compositor_private();
        if (a && a.get_effect(EFFECT)) a.remove_effect_by_name(EFFECT);
    });
}
