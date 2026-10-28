// Doorway rice — panel B "merge when maximised" (see ~/rice/README.md, #9).
// While a maximised or tiled window on the panel's monitor (current workspace) reaches the
// panel, the panel gets the style class "doorway-solid"; cinnamon.extra.css then fills the
// strip with the title-bar colour and flattens the islands. Free-floating windows never count,
// even when dragged up against the panel. Mockups: ~/rice/preview/panel-max-*.png, panel-case-*.png
const Main = imports.ui.main;
const Meta = imports.gi.Meta;
const GLib = imports.gi.GLib;

const CLASS = 'doorway-solid';
let wmIds = [], displayIds = [], pending = 0;

function touches(win, area) {
    if (win.minimized || win.get_window_type() !== Meta.WindowType.NORMAL) return false;
    if (!win.get_maximized() && !win.tile_mode) return false;
    return win.get_frame_rect().y <= area.y + 2;      // bottom tiles don't reach the panel
}

function update() {
    pending = 0;
    let ws = global.workspace_manager.get_active_workspace();
    for (let panel of Main.panelManager.panels) {
        if (!panel) continue;
        let area = ws.get_work_area_for_monitor(panel.monitorIndex);
        let solid = ws.list_windows().some(w => w.get_monitor() === panel.monitorIndex && touches(w, area));
        if (solid) panel.actor.add_style_class_name(CLASS);
        else panel.actor.remove_style_class_name(CLASS);
    }
    return GLib.SOURCE_REMOVE;
}

function queue() {
    if (!pending) pending = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 60, update);
}

function init(metadata) {}

function enable() {
    for (let sig of ['size-change', 'size-changed', 'minimize', 'unminimize', 'map', 'destroy', 'switch-workspace'])
        wmIds.push(global.window_manager.connect(sig, queue));
    for (let sig of ['grab-op-end', 'window-entered-monitor', 'window-left-monitor', 'restacked'])
        displayIds.push(global.display.connect(sig, queue));
    update();
}

function disable() {
    wmIds.forEach(id => global.window_manager.disconnect(id));
    displayIds.forEach(id => global.display.disconnect(id));
    wmIds = []; displayIds = [];
    if (pending) GLib.source_remove(pending);
    pending = 0;
    for (let panel of Main.panelManager.panels)
        if (panel) panel.actor.remove_style_class_name(CLASS);
}
