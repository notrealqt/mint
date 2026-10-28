// Doorway rice — window gaps (see ~/rice/README.md, #19).
// 1. Panel gap: an invisible strut GAP px taller than each top panel, so maximised and tiled
//    windows start GAP px below it.
// 2. Tile gap: muffin forces tiled windows to fill their tile exactly, so instead each tiled
//    window gets a shader that hides GAP px on any left/top edge facing another tile and
//    rounds its corners by RADIUS (a plain clip can only cut square corners) — see shaderSafe()
//    for the windows that have to fall back to a plain square clip.
// 3. Every other normal window / dialog gets 8px rounded corners (shadow kept);
//    maximised and fullscreen windows stay square.
// Stage px are 2x (fractional scaling): GAP 8 = 4px, RADIUS 6 = 3px.
const Main = imports.ui.main;
const Meta = imports.gi.Meta;
const St = imports.gi.St;
const GLib = imports.gi.GLib;
const Clutter = imports.gi.Clutter;
const GObject = imports.gi.GObject;

const GAP = 8, RADIUS = 6, EFFECT = 'doorway-round';
// floating windows: all four corners at the theme's 8px (= 16), the same curve GTK gives
// title bars, so apps that draw their own square top (Firefox) match; the theme's
// 1px (= 2) outline is redrawn along the curve
const FLOAT_RADIUS = 16, OUTLINE = 2;
const ROUNDED = [Meta.WindowType.NORMAL, Meta.WindowType.DIALOG, Meta.WindowType.MODAL_DIALOG];
// x0..y1 = the visible box in stage pixels.
const SHADER = `
uniform sampler2D tex;
uniform float sh, x0, y0, x1, y1, rt, rb, ow, keep, on;
void main() {
    vec2 st = cogl_tex_coord_in[0].st;
    vec4 c = texture2D(tex, st);
    if (on < 0.5) { cogl_color_out = c * cogl_color_in; return; }
    // p = stage pixel (gl_FragCoord counts from the bottom). Texture coords can't be trusted:
    // the offscreen texture is cut at the screen edge when the window hangs past it.
    vec2 p = vec2(gl_FragCoord.x, sh - gl_FragCoord.y);
    bool upper = p.y < (y0 + y1) * 0.5;
    float r = upper ? rt : rb;
    float o = upper ? 0.0 : ow;   // GTK already draws the outline round the top corners
    bool inBox = p.x >= x0 && p.y >= y0 && p.x <= x1 && p.y <= y1;
    float m = ow + 4.0;   // the theme's square outline and its shadow edge sit just outside the box
    bool nearBox = p.x >= x0 - m && p.y >= y0 - m && p.x <= x1 + m && p.y <= y1 + m;
    vec2 k = clamp(p, vec2(x0 + r, y0 + r), vec2(x1 - r, y1 - r));
    if (r > 0.0 && k.x != p.x && k.y != p.y && nearBox) {
        // corner: content inside the arc, an ow-wide outline on it, and past that the shadow
        // borrowed from the straight edge at the same distance (keep = 0: nothing, for tiles)
        float dist = length(p - k);
        float ain = clamp(r + 0.5 - dist, 0.0, 1.0), aout = clamp(r + o + 0.5 - dist, 0.0, 1.0);
        vec2 q = vec2(k.x, k.y + sign(p.y - k.y) * dist);
        vec2 dst = vec2(dFdx(st.x), -dFdy(st.y));   // texture step per stage pixel
        vec4 shadow = texture2D(tex, st + (q - p) * dst) * keep;
        cogl_color_out = (c * ain + vec4(0.0, 0.0, 0.0, 0.75) * (aout - ain) + shadow * (1.0 - aout)) * cogl_color_in;
    } else {
        // outside the box: floating windows keep their shadow (keep = 1), tiles hide it in the gap
        cogl_color_out = c * cogl_color_in * (inBox ? 1.0 : keep);
    }
}`;
// a whole number would reach GL as an int uniform; nudge it so GJS sends a double
const f = n => n + 0.0001;
let closing = new Set(), struts = [], panelIds = [], winIds = new Map(), sigs = [], pending = 0, settle = 0, rebuildId = 0;

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

// A ShaderEffect that refreshes its uniforms right before every paint, so the mask never lags
// behind a tile / snap / resize. (A static per-class shader left some windows blank, so each
// effect sets its own source.) A GType can only be registered once per Cinnamon session, so the
// class is kept on `global` under a name tied to the shader text and calls back into whatever
// `sync` this module currently provides.
function roundEffectClass() {
    let hash = 0;
    for (let i = 0; i < SHADER.length; i++) hash = (hash * 31 + SHADER.charCodeAt(i)) >>> 0;
    let name = 'DoorwayRoundEffectI' + hash.toString(16);
    global._doorwayRound = global._doorwayRound || {};
    if (!global._doorwayRound[name])
        global._doorwayRound[name] = GObject.registerClass({ GTypeName: name }, class extends Clutter.ShaderEffect {
            vfunc_paint_target(ctx) {
                if (this._sync) this._sync(this);
                super.vfunc_paint_target(ctx);
            }
        });
    return global._doorwayRound[name];
}

// Runs inside Cinnamon's paint: only plain geometry getters here. Anything that looks up the
// window's monitor segfaults Cinnamon when the window is closing (it has no monitor any more),
// so the work area is looked up in clip() and cached on the effect.
function sync(effect) {
    let actor = effect.get_actor(), win = actor && actor.meta_window, area = effect._area;
    if (!win || !area || effect._dead) {
        effect.set_uniform_value('on', f(0));
        return;
    }
    // while a tile / maximise animation scales the window, just show it unmasked
    let [sx, sy] = actor.get_scale();
    if (Math.abs(sx - 1) > 0.001 || Math.abs(sy - 1) > 0.001) {
        effect.set_uniform_value('on', f(0));
        return;
    }
    let fr = win.get_frame_rect(), b = win.get_buffer_rect(), tiled = effect._tiled;
    let left = tiled && fr.x > area.x ? GAP : 0, top = tiled && fr.y > area.y ? GAP : 0;
    // frame box on the stage, following the actor if it is being moved by an animation
    let [ax, ay] = actor.get_transformed_position();
    let ox = ax + fr.x - b.x, oy = ay + fr.y - b.y;
    effect.set_uniform_value('on', f(1));
    effect.set_uniform_value('sh', f(global.stage.height));
    effect.set_uniform_value('x0', f(ox + left));
    effect.set_uniform_value('y0', f(oy + top));
    effect.set_uniform_value('x1', f(ox + fr.width));
    effect.set_uniform_value('y1', f(oy + fr.height));
    effect.set_uniform_value('rt', f(tiled ? RADIUS : FLOAT_RADIUS));
    effect.set_uniform_value('rb', f(tiled ? RADIUS : FLOAT_RADIUS));
    effect.set_uniform_value('ow', f(tiled ? 0 : OUTLINE));
    effect.set_uniform_value('keep', f(tiled ? 0 : 1));
}

// Cinnamon's offscreen rendering drops the bottom/right rows of a window whose buffer starts above
// or left of the stage (an app's invisible border hanging off the screen edge): as many rows as
// it hangs over. That only shows when the window also reaches the far screen edge — e.g. a
// full-height tile on the external monitor (no panel there). Those windows skip the shader and
// get a plain clip: gap kept, corners square.
function shaderSafe(win) {
    let fr = win.get_frame_rect(), b = win.get_buffer_rect();
    let lostY = b.y < 0 && fr.y + fr.height > global.stage.height + b.y;
    let lostX = b.x < 0 && fr.x + fr.width > global.stage.width + b.x;
    return !lostX && !lostY;
}

function squareClip(win, actor, area) {
    let fr = win.get_frame_rect(), b = win.get_buffer_rect();
    let left = fr.x > area.x ? GAP : 0, top = fr.y > area.y ? GAP : 0;
    actor.set_clip(fr.x - b.x + left, fr.y - b.y + top, fr.width - left, fr.height - top);
}

function unround(actor) {
    let effect = actor.get_effect(EFFECT);
    if (effect) {
        effect._dead = true;
        actor.remove_effect(effect);
    }
    if (actor.has_clip) actor.remove_clip();
}

function clip(win) {
    let actor = win.get_compositor_private();
    if (!actor) return;
    if (closing.has(win) || win.get_monitor() < 0) {
        unround(actor);
        return;
    }
    let area = win.get_work_area_current_monitor();
    area = { x: area.x, y: area.y };
    let effect = actor.get_effect(EFFECT);
    let wanted = ROUNDED.includes(win.get_window_type()) && !win.is_fullscreen() &&
                 win.get_maximized() !== Meta.MaximizeFlags.BOTH;
    let safe = wanted && shaderSafe(win);
    if (!safe && effect) actor.remove_effect(effect);
    if (wanted && !safe && win.tile_mode) squareClip(win, actor, area);
    else if (actor.has_clip) actor.remove_clip();
    if (!safe) return;
    if (!effect) {
        effect = new (roundEffectClass())({ shader_type: Clutter.ShaderType.FRAGMENT_SHADER });
        effect.set_shader_source(SHADER);
        actor.add_effect_with_name(EFFECT, effect);
    }
    effect._area = area;
    effect._tiled = !!win.tile_mode;
    effect._sync = sync;
    effect.queue_repaint();
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
    let ids = ['size-changed', 'position-changed'].map(s => win.connect(s, queueClip));
    // drop the effect the moment a window starts closing (its close animation still paints)
    ids.push(win.connect('unmanaging', () => {
        closing.add(win);
        let a = win.get_compositor_private();
        if (a) unround(a);
    }));
    ids.push(win.connect('unmanaged', () => {
        closing.delete(win);
        winIds.delete(win);
    }));
    winIds.set(win, ids);
}

function init(metadata) {}

function enable() {
    allWindows().forEach(watch);
    sigs.push([global.display, global.display.connect('window-created', (d, w) => { watch(w); queueClip(); })]);
    sigs.push([global.display, global.display.connect('workareas-changed', queueClip)]);
    // tiling a window that already has the tile's size changes no geometry, only its tile mode
    for (let sig of ['size-change', 'size-changed', 'map', 'unminimize', 'switch-workspace'])
        sigs.push([global.window_manager, global.window_manager.connect(sig, queueClip)]);
    sigs.push([global.display, global.display.connect('grab-op-end', queueClip)]);
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
    closing.clear();
    [pending, settle, rebuildId].forEach(id => { if (id) GLib.source_remove(id); });
    pending = settle = rebuildId = 0;
    clearStruts();
    allWindows().forEach(w => {
        let a = w.get_compositor_private();
        if (a) unround(a);
    });
}
