function capitalize(text){
  return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
}

function initializeReports(){
  let text = "";
  reportList.forEach(item => {
    let date = new Date(Number(item["report_date"])).toISOString().slice(0, 19).replace(/-/g, "/").replace("T", " ");
    let app_name = capitalize(item.app_name)

    let addLetter = item.artifacts !== 1 ? "s" : ""

    text += `<a href="../../ModuleOutput/AndroidForensics/${item.link}" class="text-muted list-group-item list-group-item-action">`;
    text += `<div class="py-1 mb-0 small">`;
    text += `<div class="d-flex justify-content-between align-items-center w-100">`;
    text += `<strong class="text-gray-dark">Report for ${app_name} (${item.app_id})</strong>`;
    text += `<span>${item.artifacts} artifact${addLetter}</span>`
    text += `</div>`;
    text += `<span class="d-block">Generated at ${date}</span>`;
    
    text += `</div>`;
    text += `</a>`;
  });

  $("#reports-list").html(text);
}

(function () {
  'use strict'
  initializeReports()

}())
