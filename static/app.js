const entrance = document.getElementById('main-app');
const inputField1 = document.getElementById('username');
const inputField2 = document.getElementById('Room_Name');
const text = document.getElementById('iptext');
const contentElement = document.querySelector('.content');
const btn = document.querySelector('#submit-btn'); 

function check(){
  if (inputField1.value === '' || inputField2.value === ''){
    text.textContent = 'Please Create a room or join || create a room number';
    text.style.color = 'red';
    text.style.fontSize = '20px';
    btn.disabled = true;
    
  } else{
    text.textContent = '';
    text.style.color = 'none';
    text.style.fontSize = 'none';
    btn.disabled = false;
  }
}

btn.addEventListener('click', check);

