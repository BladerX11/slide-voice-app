import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

import SlideVoiceApp

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
    title: "Slide Voice App"

    menuBar: MenuBar {
        Menu {
            title: "Menu"

            Action {
                text: "Settings"
                onTriggered: settingsLoader.active = true
            }
        }
    }

    // Settings window loader
    Loader {
        id: settingsLoader
        active: false
        source: "SettingsWindow.qml"

        onLoaded: {
            item.visible = true;
        }
    }

    Connections {
        target: settingsLoader.item

        function onClosing() {
            settingsLoader.active = false;
        }
    }

    // Dummy data model for slides
    ListModel {
        id: slideModel

        ListElement {
            notes: "These are the notes for Slide 1.\n\nYou can edit them here."
        }
        ListElement {
            notes: "Notes for Slide 2 go here.\n\nThis slide covers the main topic."
        }
        ListElement {
            notes: "Slide 3 contains supporting details.\n\nRemember to mention the key points."
        }
        ListElement {
            notes: "Final slide with conclusions.\n\nThank the audience!"
        }
    }

    ListModel {
        id: providerModel
    }

    ListModel {
        id: voiceModel
    }

    Connections {
        target: TTSManager

        function onVoicesReady(voices) {
            voiceModel.clear();
            const st = voices.forEach(voice => voiceModel.append(voice));
            voiceComboBox.currentIndex = voiceModel.count > 0 ? 0 : -1;
        }

        function onErrorOccurred(message) {
            errorDialog.text = message;
            errorDialog.open();
        }
    }

    MessageDialog {
        id: errorDialog
        title: "Error"
        buttons: MessageDialog.Ok
    }

    Component.onCompleted: {
        let providers = TTSManager.getAvailableProviders();
        providers.forEach(provider => providerModel.append(provider));

        if (providerModel.count > 0) {
            providerComboBox.currentIndex = 0;
            TTSManager.setProvider(providerComboBox.currentValue);
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Left pane: Slide list
        ListView {
            id: slideList
            Layout.preferredWidth: 160
            Layout.fillHeight: true
            model: slideModel
            spacing: 10

            delegate: Rectangle {
                id: slideItem
                width: 140
                height: 40
                anchors.horizontalCenter: parent.horizontalCenter
                radius: 4
                border.width: ListView.isCurrentItem ? 3 : 0
                border.color: palette.highlight

                Text {
                    anchors.centerIn: parent
                    text: `Slide ${model.index + 1}`
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        slideItem.ListView.view.currentIndex = model.index;
                    }
                }
            }
        }

        // Right pane: Notes editor and controls
        ColumnLayout {
            spacing: 10

            // Notes text area
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true

                TextArea {
                    id: notesEditor
                    placeholderText: "Slide notes..."
                    wrapMode: TextArea.Wrap

                    Connections {
                        target: slideList

                        function onCurrentIndexChanged() {
                            notesEditor.text = slideModel.get(slideList.currentIndex)?.notes ?? "";
                        }
                    }

                    onTextChanged: {
                        if (activeFocus && slideList.currentIndex > 0) {
                            slideModel.setProperty(slideList.currentIndex, "notes", text);
                        }
                    }
                }
            }

            // Controls row
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                ComboBox {
                    id: providerComboBox
                    model: providerModel
                    textRole: "name"
                    valueRole: "id"
                    displayText: currentIndex >= 0 ? currentText : "Provider"
                    enabled: !TTSManager.isGenerating && !TTSManager.isFetchingVoices

                    onCurrentIndexChanged: {
                        if (currentIndex >= 0) {
                            // curretValue is not set at startup, so use model lookup
                            TTSManager.setProvider(providerModel.get(currentIndex).id);
                        }
                    }
                }

                ComboBox {
                    id: voiceComboBox
                    Layout.preferredWidth: 300
                    model: voiceModel
                    valueRole: "id"
                    textRole: "name"
                    enabled: !TTSManager.isGenerating && !TTSManager.isFetchingVoices

                    displayText: {
                        if (TTSManager.isFetchingVoices) {
                            return "Loading...";
                        }

                        if (currentIndex >= 0) {
                            return currentText;
                        }

                        return "Voice";
                    }

                    delegate: ItemDelegate {
                        width: voiceComboBox.width
                        text: `${model.name} (${model.languageCode}, ${model.gender})`
                    }
                }

                Item {
                    Layout.fillWidth: true
                }

                Button {
                    text: TTSManager.isPlaying ? "Stop" : "Preview"
                    enabled: !TTSManager.isGenerating && !TTSManager.isFetchingVoices && voiceComboBox.currentIndex >= 0 && notesEditor.text.trim().length > 0

                    onClicked: {
                        if (TTSManager.isPlaying) {
                            TTSManager.stopAudio();
                        } else {
                            let languageCode = voiceModel.get(voiceComboBox.currentIndex).languageCode;
                            TTSManager.generateAndPlay(notesEditor.text, voiceComboBox.currentValue, languageCode);
                        }
                    }
                }

                Button {
                    text: "Save PPTX"
                    enabled: !TTSManager.isGenerating
                    onClicked: {
                        console.log("Save PPTX file");
                    }
                }
            }
        }
    }

    footer: RowLayout {
        BusyIndicator {
            running: TTSManager.isGenerating || TTSManager.isFetchingVoices
            Layout.preferredHeight: 20
            Layout.preferredWidth: 20
        }

        Label {
            Layout.fillWidth: true
            text: {
                if (TTSManager.isGenerating) {
                    return "Generating audio...";
                }

                if (TTSManager.isFetchingVoices) {
                    return "Fetching voices...";
                }

                if (TTSManager.isPlaying) {
                    return "Playing audio...";
                }

                return "";
            }
        }
    }
}
