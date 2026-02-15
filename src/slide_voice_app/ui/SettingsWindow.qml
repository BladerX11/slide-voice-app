import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtCore

import SlideVoiceApp

ApplicationWindow {
    id: settingsWindow
    title: "Settings"
    width: 500
    height: 400
    modality: Qt.ApplicationModal
    flags: Qt.Dialog

    ListModel {
        id: providerModel
    }

    ListModel {
        id: settingsModel
    }

    Settings {
        id: appSettings
    }

    function settingsKey(providerId, key) {
        return providerId + "/" + key;
    }

    Component.onCompleted: {
        let providers = TTSManager.getAvailableProviders();
        providers.forEach(provider => providerModel.append(provider));

        if (providerModel.count > 0) {
            providerComboBox.currentIndex = 0;
            loadProviderSettings(providerComboBox.currentValue);
        }
    }

    function loadProviderSettings(providerId) {
        settingsModel.clear();
        TTSManager.getProviderSettings(providerId).forEach(setting => settingsModel.append(setting));
    }

    function saveSettings() {
        if (providerComboBox.currentIndex < 0)
            return;

        let providerId = providerComboBox.currentValue;

        for (let i = 0; i < settingsModel.count; i++) {
            let setting = settingsModel.get(i);
            appSettings.setValue(settingsKey(providerId, setting.key), setting.value);
        }

        TTSManager.setProvider(providerId);
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Provider selector
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Label {
                text: "Provider:"
            }

            ComboBox {
                id: providerComboBox
                Layout.fillWidth: true
                model: providerModel
                textRole: "name"
                valueRole: "id"

                onCurrentIndexChanged: {
                    if (currentIndex >= 0) {
                        // currentValue not set on first run
                        settingsWindow.loadProviderSettings(providerModel.get(currentIndex).id);
                    }
                }
            }
        }

        // Dynamic settings form
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 15
            model: settingsModel
            delegate: RowLayout {
                id: settingList
                required property string label
                required property string value
                required property string type
                required property string placeholder
                required property var model

                width: parent.width
                spacing: 5

                Label {
                    text: settingList.label
                }

                TextField {
                    Layout.fillWidth: true
                    text: settingList.value
                    placeholderText: settingList.placeholder
                    echoMode: settingList.type === "password" ? TextInput.Password : TextInput.Normal

                    onTextChanged: settingList.ListView.view.model.setProperty(settingList.model.index, "value", text)
                }
            }
        }

        // Buttons
        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 10

            Button {
                text: "Cancel"
                onClicked: settingsWindow.close()
            }

            Button {
                text: "Save"
                highlighted: true
                onClicked: {
                    settingsWindow.saveSettings();
                    settingsWindow.close();
                }
            }
        }
    }
}
