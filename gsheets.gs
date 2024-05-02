function processNewRow(e) {
  var spreadsheet = e.source;
  var sheet = spreadsheet.getSheetByName("FAFLog");
  var lastRow = sheet.getLastRow();
  
  var scriptProperties = PropertiesService.getScriptProperties();
  var lastProcessedRow = Number(scriptProperties.getProperty('LAST_PROCESSED_ROW')) || 0;

  if (lastRow > lastProcessedRow) {
    for (var i = lastProcessedRow + 1; i <= lastRow; i++) {
      var cell = sheet.getRange(i, 5);
      var cellValue = cell.getValue();
      var command;
      try {
        command = JSON.parse(cellValue);
      } catch (error) {
        return;
      }
      
      // process the command
      switch(command.command) {
        case "follow_up_then":
          sendFollowUpEmail(command.payload);
          break;
        case "user_note":
          sendSelfNoteEmail(command.payload);
          break;
        case "save_url":
          saveUrl(command.payload);
          break;
        default:
      }
    }
    scriptProperties.setProperty('LAST_PROCESSED_ROW', lastRow.toString());
  }
}


function sendFollowUpEmail(payload) {
  var date = payload.date;
  var message = payload.message;
  
  // replace with your followupthen.com email address
  var email = date+"@followupthen.com";
  
  MailApp.sendEmail({
    to: email,
    subject: message,
    body: "Send from FAF"
  });
}

function sendSelfNoteEmail(payload) {
  var message = payload.message;
  
  // get the email address of the currently active user
  var email = Session.getActiveUser().getEmail();
  
  MailApp.sendEmail({
    to: email,
    subject: "[Self Note] " + message,
    body: "Send from FAF"
  });
}

function saveUrl(payload) {
    var url = payload.url;
    
    // replace with the ID of your separate Google Sheets file
    var sheetId = "your-google-sheets-id";
    
    var sheet = SpreadsheetApp.openById(sheetId).getActiveSheet();
    sheet.appendRow([url]);
  }
  
