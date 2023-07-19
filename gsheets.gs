function processNewRow(e) {
  var spreadsheet = e.source;
  
  // get the sheet by name
  var sheet = spreadsheet.getSheetByName("FAFLog");
  
  // get the last row in the sheet
  var lastRow = sheet.getLastRow();
  
  // get the 'JSON command' cell in the last row
  var cell = sheet.getRange(lastRow, 5);
  
  // get the value of the cell
  var cellValue = cell.getValue();
  
  // parse JSON string
  var command;
  try {
    command = JSON.parse(cellValue);
  } catch (error) {
    // handle error
    return;
  }
  
  // process the command
  switch(command.command) {
    case "follow_up_then":
      sendFollowUpEmail(command.payload);
      break;
    case "note_to_self":
      sendSelfNoteEmail(command.payload);
      break;
    case "save_url":
      saveUrl(command.payload);
      break;
    default:
      // unknown command
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
  
