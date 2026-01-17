import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
    title: "Slide Voice App"

    // Dummy data model for slides
    ListModel {
        id: slideModel

        ListElement {
            slideName: "Slide 1"
            notes: "These are the notes for Slide 1.\n\nYou can edit them here."
            thumbnailColor: "#3498db"
        }
        ListElement {
            slideName: "Slide 2"
            notes: "Notes for Slide 2 go here.\n\nThis slide covers the main topic."
            thumbnailColor: "#e74c3c"
        }
        ListElement {
            slideName: "Slide 3"
            notes: "Slide 3 contains supporting details.\n\nRemember to mention the key points."
            thumbnailColor: "#2ecc71"
        }
        ListElement {
            slideName: "Slide 4"
            notes: "Final slide with conclusions.\n\nThank the audience!"
            thumbnailColor: "#9b59b6"
        }
    }

    // Dummy data for providers
    ListModel {
        id: providerModel
        ListElement {
            name: "OpenAI"
        }
        ListElement {
            name: "ElevenLabs"
        }
        ListElement {
            name: "Azure"
        }
        ListElement {
            name: "Google Cloud"
        }
    }

    // Dummy data for voices
    ListModel {
        id: voiceModel
        ListElement {
            name: "Alloy"
        }
        ListElement {
            name: "Echo"
        }
        ListElement {
            name: "Fable"
        }
        ListElement {
            name: "Nova"
        }
        ListElement {
            name: "Onyx"
        }
        ListElement {
            name: "Shimmer"
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

            delegate: Item {
                id: slideItemRoot
                width: slideItem.width
                height: slideItem.height
                anchors.horizontalCenter: parent.horizontalCenter

                Column {
                    id: slideItem
                    spacing: 4

                    // Thumbnail placeholder
                    Rectangle {
                        width: 140
                        height: 90
                        color: model.thumbnailColor
                        radius: 4
                        border.width: slideItemRoot.ListView.isCurrentItem ? 3 : 1
                        border.color: slideItemRoot.ListView.isCurrentItem ? palette.highlight : palette.mid

                        Text {
                            anchors.centerIn: parent
                            text: "Slide " + (model.index + 1) + " Image"
                            font.pixelSize: 12
                        }
                    }

                    // Slide label
                    Text {
                        id: slideLabel
                        text: model.slideName
                        width: parent.width
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: 14
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        slideItemRoot.ListView.view.currentIndex = model.index;
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
                    displayText: currentIndex >= 0 ? providerModel.get(currentIndex).name : "Provider"
                }

                ComboBox {
                    id: voiceComboBox
                    model: voiceModel
                    displayText: currentIndex >= 0 ? voiceModel.get(currentIndex).name : "Voice"
                }

                Item {
                    Layout.fillWidth: true
                }

                Button {
                    text: "Preview"
                    onClicked: {
                        console.log("Preview audio for slide", slideList.currentIndex + 1);
                    }
                }

                Button {
                    text: "Save Audio"
                    onClicked: {
                        console.log("Save audio to slide", slideList.currentIndex + 1);
                    }
                }

                Button {
                    text: "Save PPTX"
                    onClicked: {
                        console.log("Save PPTX file");
                    }
                }
            }
        }
    }
}
