var groupButtonExample = document.getElementsByClassName("form-settings__group-color-example")[0];
var colorPicker = document.getElementsByClassName("form-settings__group-color")[0];
var colorPickerImg = document.getElementsByClassName("form-settings__color-picker-img")[0];
groupButtonExample.style.backgroundColor = colorPicker.value;

colorPicker.onchange = function() {
    groupButtonExample.style.backgroundColor = colorPicker.value;
}

colorPickerImg.addEventListener('click', function (e) {
    colorPicker.click()
  });