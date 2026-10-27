// Doorway rice — hide tray icons that clutter the panel (see ~/rice/README.md, #9).
// Cinnamon hides any tray/XApp status icon whose name is registered as "replaced by an applet",
// so claiming the names here hides them; disabling the extension brings them back.
// The apps keep running (Update Manager still checks, NVIDIA Prime still switches, …).
const Main = imports.ui.main;

const UUID = 'doorway-tray@notrealqt';
const HIDE = ['mintupdate.py', 'mintreport', 'process-monitor', 'nvidia-prime'];

function init(metadata) {}

function enable() {
    for (let role of HIDE)
        Main.systrayManager.registerTrayIconReplacement(role, UUID);
}

function disable() {
    Main.systrayManager.unregisterTrayIconReplacement(UUID);
}
