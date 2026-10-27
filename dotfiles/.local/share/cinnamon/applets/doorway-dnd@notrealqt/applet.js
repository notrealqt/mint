// Doorway rice — do-not-disturb bell for the panel (#9 in ~/rice/README.md).
// Click toggles Cinnamon's "show notifications" setting; the bell turns into a crossed-out
// orange bell while notifications are silenced. Missed ones still collect in the notifications applet.
const Applet = imports.ui.applet;
const Gio = imports.gi.Gio;

const KEY = 'display-notifications';

class DoorwayDnd extends Applet.IconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this._settings = new Gio.Settings({ schema_id: 'org.cinnamon.desktop.notifications' });
        this._changedId = this._settings.connect('changed::' + KEY, () => this._update());
        this._update();
    }

    _update() {
        let on = this._settings.get_boolean(KEY);
        this.set_applet_icon_symbolic_name(on ? 'notification-symbolic' : 'notifications-disabled-symbolic');
        this.set_applet_tooltip(on ? 'Notifications on — click for Do not disturb' : 'Do not disturb — click to turn notifications back on');
        // orange while silenced, so it's obvious at a glance
        this._applet_icon.set_style(on ? '' : 'color: #e39236;');
    }

    on_applet_clicked() {
        this._settings.set_boolean(KEY, !this._settings.get_boolean(KEY));
    }

    on_applet_removed_from_panel() {
        this._settings.disconnect(this._changedId);
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new DoorwayDnd(metadata, orientation, panelHeight, instanceId);
}
