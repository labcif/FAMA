function capitalize(text){
  return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
}

function initializeReports(){
  let text = "";
  reportList["reports"].forEach(item => {
    let date = new Date(Number(item["report_date"])).toISOString().slice(0, 19).replace(/-/g, "/").replace("T", " ");
    let app_name = capitalize(item.app_name)

    let addLetter = item.artifacts !== 1 ? "s" : ""

    text += `<a href="${item.link}" class="text-muted list-group-item list-group-item-action">
      <div class="py-1 mb-0 small">
        <div class="d-flex justify-content-between align-items-center w-100">
          <strong class="text-gray-dark">Report for ${app_name} (${item.app_id})</strong>
          <span>${item.artifacts} artifact${addLetter}</span>
        </div>
        <span class="d-block">Generated at ${date}</span>
      </div>
    </a>`;
  });

  $("#reports-list").html(text);
}

function initializeCaseInfo(){
  if (!reportList.case_name && !reportList.case_number && !reportList.examiner){
    return
  }
  
  let text = `<h6 class="pb-2 mb-0">Case Information</h6>`;

  if (reportList.case_name){
    text += `<div class="text-muted small"><strong>Case Name: </strong>${reportList.case_name}</div>`;
  }

  if (reportList.case_number){
    text += `<div class="text-muted small"><strong>Case Number: </strong>${reportList.case_number}</div>`;
  }

  if (reportList.examiner){
    text += `<div class="text-muted small"><strong>Examiner: </strong>${reportList.examiner}</div>`;
  }

  $("#case-info").html(text);
}

(function () {
  'use strict'
  initializeCaseInfo()
  initializeReports()

}())
