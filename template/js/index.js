function capitalize(text){
  return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
}

function initializeReports(){
  let text = "";
  reportList.forEach(item => {
    let date = new Date(Number(item["report_date"])).toISOString().slice(0, 19).replace(/-/g, "/").replace("T", " ");
    let app_name = capitalize(item.app_name)

    let addLetter = item.artifacts !== 1 ? "s" : ""

    text += `<a href="../../ModuleOutput/AndroidForensics/${item.link}" class="text-muted list-group-item list-group-item-action">
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

(function () {
  'use strict'
  initializeReports()

}())
