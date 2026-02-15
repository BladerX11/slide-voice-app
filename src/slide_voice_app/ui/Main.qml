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
            title: "File"

            Action {
                text: "Open"
                onTriggered: fileDialog.open()
            }

            Action {
                text: "Save"
                enabled: PPTXManager.fileLoaded
                onTriggered: saveDialog.open()
            }

            Action {
                text: "Settings"
                onTriggered: settingsLoader.active = true
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "Open PowerPoint File"
        nameFilters: ["PowerPoint files (*.pptx)"]
        onAccepted: PPTXManager.openFile(selectedFile)
    }

    FileDialog {
        id: saveDialog
        title: "Export PowerPoint File"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PowerPoint files (*.pptx)"]
        onAccepted: PPTXManager.exportTo(selectedFile)
    }

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

    ListModel {
        id: slideModel
    }

    ListModel {
        id: providerModel
    }

    ListModel {
        id: voiceModel
    }

    Connections {
        target: PPTXManager

        function onSlidesLoaded(slides) {
            slideModel.clear();
            slides.forEach(slide => slideModel.append(slide));
            slideList.currentIndex = slideModel.count > 0 ? 0 : -1;
        }

        function onErrorOccurred(message) {
            errorDialog.text = message;
            errorDialog.open();
        }
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
            Layout.preferredWidth: 140
            Layout.fillHeight: true
            model: slideModel
            spacing: 10

            delegate: Rectangle {
                id: slideItem
                required property var model

                width: ListView.view.width
                height: 40
                radius: 4
                border.width: ListView.isCurrentItem ? 3 : 0
                border.color: palette.highlight

                Text {
                    anchors.centerIn: parent
                    text: `Slide ${slideItem.model.index + 1}`
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        slideItem.ListView.view.currentIndex = slideItem.model.index;
                    }
                }
            }

            onCurrentIndexChanged: {
                TTSManager.currentSlideHasAudio = false;
                notesEditor.text = slideModel.get(slideList.currentIndex)?.notes ?? "";
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

                    onTextChanged: {
                        if (activeFocus && slideList.currentIndex >= 0) {
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
                        required property string name
                        required property string languageCode
                        required property string gender

                        width: ListView.view.width
                        text: `${name} (${languageCode}, ${gender})`
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
                    text: "Insert Audio"
                    enabled: !TTSManager.isGenerating && PPTXManager.fileLoaded && TTSManager.currentSlideHasAudio
                    onClicked: {
                        PPTXManager.saveAudioForSlide(slideList.currentIndex, TTSManager.outputFile);
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
