import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtCore

import SlideVoiceApp

Window {
    id: settingsWindow
    title: "Settings"
    width: 500
    height: 400
    modality: Qt.ApplicationModal
    flags: Qt.Dialog

    property var pendingChanges: ({})

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
        providers.forEach(function (provider) {
            providerModel.append(provider);
        });

        if (providerModel.count > 0) {
            providerComboBox.currentIndex = 0;
            loadProviderSettings(providerComboBox.currentValue);
        }
    }

    function loadProviderSettings(providerId) {
        settingsModel.clear();
        pendingChanges = {};
        TTSManager.getProviderSettings(providerId).forEach(setting => settingsModel.append(setting));
    }

    function saveSettings() {
        if (providerComboBox.currentIndex < 0)
            return;

        let providerId = providerComboBox.currentValue;

        for (let key in pendingChanges) {
            appSettings.setValue(settingsKey(providerId, key), pendingChanges[key]);
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
                width: parent.width
                spacing: 5

                Label {
                    text: model.label
                }

                TextField {
                    Layout.fillWidth: true
                    text: model.value
                    placeholderText: model.placeholder
                    echoMode: model.type === "password" ? TextInput.Password : TextInput.Normal

                    onTextChanged: {
                        settingsWindow.pendingChanges[model.key] = text;
                    }
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
