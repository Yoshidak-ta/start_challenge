function waitForServiceWorkerReady(attempts = 10) {
  return new Promise((resolve, reject) => {
      let checkInterval = setInterval(() => {
          navigator.serviceWorker.ready.then((registration) => {
              if (registration.active) {
                  console.log("Service Worker がアクティブになりました", registration);
                  clearInterval(checkInterval);
                  resolve(registration);
              }
          }).catch(reject);

          attempts--;
          if (attempts <= 0) {
              clearInterval(checkInterval);
              reject(new Error("Service Worker がアクティブになりませんでした"));
          }
      }, 1000);
  });
}

function getCsrfToken() {
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || 
                    document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  if (!csrfToken) {
      console.error("CSRFトークンが見つかりませんでした");
  }
  return csrfToken;
}

// Webプッシュ通知登録
document.addEventListener('DOMContentLoaded', function () {
  console.log('通知設定読み込み');
  const enableBtn = document.getElementById('enableNotifications');
  const disableBtn = document.getElementById('disableNotifications');

  // 通知設定状況を確認し表示するボタンを切り替える
  console.log(Notification.permission);
  if (Notification.permission === 'granted') {
      disableBtn.style.display = 'block';
  } else {
      enableBtn.style.display = 'block';
  }

  // 通知を有効にする処理
  enableBtn.addEventListener('click', () => {
    Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
            console.log('通知が許可されました');

            // Service Workerを登録
            navigator.serviceWorker.register('/sw.js').then((registration) => {
              console.log('Service Worker 登録完了', registration);

              return navigator.serviceWorker.ready;
            }).then((registration) => {
              console.log('Service Worker がアクティブになりました', registration);

              // プッシュ通知の購読を開始
              return registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: 'BHJYaOwq1s3Tu18w6gr1o0hF7_P7NQHTI8k-S4z2dNTVZoZvjQBUi73ssZNe1NEQRYPBwa09befpLFz33ZipktU'
              });
            }).then(subscription => {
              console.log('プッシュ通知の購読成功', subscription);

              return fetch('/api/save-subscription/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(subscription)
            });
          }).then(response => {
            if (response.ok) {
              console.log('サーバーへの登録成功');
              enableBtn.style.display = 'none';
              disableBtn.style.display = 'block';
            } else {
              console.log('サーバー登録エラー：', response.statusText);
            }
          }).catch(error => {
              console.error("プッシュ通知の登録に失敗:", error);
          });
        } else {
            console.log('通知が拒否されました');
        }
    });
  });

  // Service Worker 更新を強制実行
  navigator.serviceWorker.getRegistration().then((registration) => {
      if (registration) {
          registration.update().then(() => {
              console.log("Service Worker を手動更新しました");
          });
      }
  });

  // 通知を無効にする処理
  disableBtn.addEventListener("click", () => {
    console.log('通知無効ボタンを押下')
    navigator.serviceWorker.ready.then((registration) => {
      registration.pushManager.getSubscription().then((subscription) => {
        if (subscription) {
          subscription.unsubscribe().then((success) => {
            if (success) {
              console.log("通知を無効にしました。");
              
              // Django サーバーにも解除を通知
              fetch("/api/unregister-subscription/", {
                method: "POST",
                body: JSON.stringify({ "endpoint": subscription.endpoint }),
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCsrfToken()
                }
              }).then(response => {
                console.log("送信データ:", JSON.stringify({ "endpoint": subscription.endpoint })); 
                if (response.ok) {
                  console.log("通知解除成功");
                  disableBtn.style.display = "none";
                  enableBtn.style.display = "block";
                } else {
                  console.error("通知解除エラー:", response.statusText);
                }
              }).catch(error => {
                console.error("サーバーへの通知解除リクエスト失敗:", error);
              });
                
            }
          }).catch((error) => {
            console.error("プッシュ通知の登録解除に失敗しました:", error);
          });
        } else {
          console.log("プッシュ通知の登録はありません。");
        }
      });
    });
  }); 
});


// 回答アコーディオン
document.addEventListener("DOMContentLoaded", function () {

  const headers = document.querySelectorAll(".card-header");

  headers.forEach(header => {
    header.addEventListener("click", function () {
      const cardId = this.getAttribute("data-card-id");
      const cardBody = document.getElementById(`card-body-${cardId}`);
      if (cardBody.style.display === "none" || cardBody.style.display === "") {
        cardBody.style.display = "block";
      } else {
        cardBody.style.display = "none";
      }
    });
  });
});

  function insertTemplate(templateId){
    const templateElement = document.getElementById(templateId);
    const templateText = templateElement.innerText || templateElement.textContent;

    const commentField = document.getElementById('comment-field');
    commentField.value = templateText;
  } 

document.addEventListener("DOMContentLoaded", function () {
  const answerButton = document.getElementById("answer-btn");
  const answerFormContainer = document.getElementById("answer-form-container");

  answerButton.addEventListener("click", function () {
    if (answerFormContainer.style.display === "none" || answerFormContainer.style.display === "") {
      answerFormContainer.style.display = "block";
    } else {
      answerFormContainer.style.display = "none";
    }
  });
});

// モーダル内ユーザ検索機能(チャットグループ)
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.chatgroup-adduser-modal').forEach(modal => {
    const searchForm = document.getElementById('chatgroupSearchForm');
    const searchInput = document.getElementById('chatgroupSearchInput');
    const userList = document.getElementById('chatgroupUserList');

    let chatgroupSelectedUsers = new Set();
  
    searchForm.addEventListener('submit', function(event) {
      event.preventDefault();

      const chatgroupSearchQuery = searchInput.value;
      fetch(`/chats/chat/search_users?search=${encodeURIComponent(chatgroupSearchQuery)}`)
        .then(response => response.json())
        .then(data => {

          modal.querySelectorAll('.user-group-checkbox').forEach(checkbox => {
            if (checkbox.checked) {
              chatgroupSelectedUsers.add(parseInt(checkbox.value));
            } else {
              chatgroupSelectedUsers.delete(parseInt(checkbox.value));
            }
          });

          userList.innerHTML = '';

          data.users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.classList.add('form-check');

            const isChecked = chatgroupSelectedUsers.has(user.id) ? 'checked' : '';

            userDiv.innerHTML = `
              <input class="form-check-input user-group-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}" ${isChecked}>
              <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
              <label class="form-check-label" for='user${user.id}'>${user.username}</label>
            `
            userList.appendChild(userDiv);
          });

          modal.querySelectorAll('.user-group-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
              if (this.checked) {
                chatgroupSelectedUsers.add(this.value);
              } else {
                chatgroupSelectedUsers.delete(this.value);
              }
            });
          });
        })
        .catch(error => console.error('Error:', error));
      });

      // モーダルが閉じられた時にデータをリセット
      modal.addEventListener('hidden.bs.modal', function () {
        chatgroupSelectedUsers.clear();
        userList.innerHTML = `
          <input class="form-check-input user-group-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}">
          <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
          <label class="form-check-label" for='user${user.id}'>${user.username}</label>
        `;
        searchInput.value = '';
      });
  });
});


// チャットグループ(ユーザ選択)
document.addEventListener('DOMContentLoaded', function () {

  const selectedUsersDisplay = document.getElementById('selectedGroupUsersDisplay');
  const selectedUsersInput = document.getElementById('selectedGroupUsers');
  const confirmUserSelectionButton = document.getElementById('addGroupUsers');

  confirmUserSelectionButton.addEventListener('click', () => {
    console.log("追加（登録）ボタンが押されました");

    const selectedUserIds = [];
    const selectedUsernames = [];
    document.querySelectorAll('.user-group-checkbox:checked').forEach((checkbox) => {
        selectedUserIds.push(parseInt(checkbox.value, 10));
        selectedUsernames.push(checkbox.getAttribute('data-name'));
    });

    console.log("選択したユーザID:", selectedUserIds);
    console.log("選択したユーザ名:", selectedUsernames);

    // 選択したユーザをフォームに反映
    if (selectedUsernames.length > 0) {
        selectedUsersDisplay.innerHTML = selectedUsernames
            .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
            .join('');

        // hidden input に選択したユーザのIDをセット
        selectedUsersInput.value = selectedUserIds.join(',');
        console.log("Hidden Input Value:", selectedUsersInput.value);
    } else {
        selectedUsersDisplay.innerHTML = '<p>ユーザが選択されていません</p>';
        selectedUsersInput.value = "";
    }

    // ユーザ選択モーダルを閉じる
    const userModalElement = document.getElementById('addGroupUserModal');
    const userModal = bootstrap.Modal.getInstance(userModalElement);
    if (userModal) {
        userModal.hide();
    }
  });
});

// モーダル内ユーザ検索機能(スケジュール登録)_chat.ver
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.schedule-adduser-modal').forEach(modal => {
    const searchForm = document.getElementById('scheduleSearchForm');
    const searchInput = document.getElementById('scheduleSearchInput');
    const userList = document.getElementById('scheduleUserList');

    let scheduleSelectedUsers = new Set();
  
    searchForm.addEventListener('submit', function(event) {
      event.preventDefault();

      const scheduleSearchQuery = searchInput.value;
      fetch(`/chats/chat/search_users?search=${encodeURIComponent(scheduleSearchQuery)}`)
        .then(response => response.json())
        .then(data => {

          modal.querySelectorAll('.user-checkbox').forEach(checkbox => {
            if (checkbox.checked) {
              scheduleSelectedUsers.add(parseInt(checkbox.value));
            } else {
              scheduleSelectedUsers.delete(parseInt(checkbox.value));
            }
          });

          userList.innerHTML = '';

          data.users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.classList.add('form-check');

            const isChecked = scheduleSelectedUsers.has(user.id) ? 'checked' : '';

            userDiv.innerHTML = `
                <input class="form-check-input user-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}" ${isChecked}>
                <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
                <label class="form-check-label" for='user${user.id}'>${user.username}</label>
            `
            userList.appendChild(userDiv);
          });

          modal.querySelectorAll('.user-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
              if (this.checked) {
                scheduleSelectedUsers.add(this.value);
              } else {
                scheduleSelectedUsers.delete(this.value);
              }
            });
          });
        })
        .catch(error => console.error('Error:', error));
    });
     // モーダルが閉じられた時にデータをリセット
     modal.addEventListener('hidden.bs.modal', function () {
      scheduleSelectedUsers.clear();
      userList.innerHTML = `
        <input class="form-check-input user-group-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}">
        <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
        <label class="form-check-label" for='user${user.id}'>${user.username}</label>
      `;
      searchInput.value = '';
    });
  });
});

// モーダル内ユーザ検索機能(スケジュール登録)_schedule.ver
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.schedule-selectuser-modal').forEach(modal => {
    const searchForm = document.getElementById('scheduleSelectSearchForm');
    const searchInput = document.getElementById('scheduleSelectSearchInput');
    const userList = document.getElementById('scheduleSelectUserList');

    let scheduleSelectedUsers = new Set();
  
    searchForm.addEventListener('submit', function(event) {
      event.preventDefault();

      const scheduleSearchQuery = searchInput.value;
      fetch(`/schedules/schedule_show/search_users?search=${encodeURIComponent(scheduleSearchQuery)}`)
        .then(response => response.json())
        .then(data => {

          modal.querySelectorAll('.user-checkbox').forEach(checkbox => {
            if (checkbox.checked) {
              scheduleSelectedUsers.add(parseInt(checkbox.value));
            } else {
              scheduleSelectedUsers.delete(parseInt(checkbox.value));
            }
          });

          userList.innerHTML = '';

          data.users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.classList.add('form-check');

            const isChecked = scheduleSelectedUsers.has(user.id) ? 'checked' : '';

            userDiv.innerHTML = `
                <input class="form-check-input user-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}" ${isChecked}>
                <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
                <label class="form-check-label" for='user${user.id}'>${user.username}</label>
            `
            userList.appendChild(userDiv);
          });

          modal.querySelectorAll('.user-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
              if (this.checked) {
                scheduleSelectedUsers.add(this.value);
              } else {
                scheduleSelectedUsers.delete(this.value);
              }
            });
          });
        })
        .catch(error => console.error('Error:', error));
    });
     // モーダルが閉じられた時にデータをリセット
     modal.addEventListener('hidden.bs.modal', function () {
      scheduleSelectedUsers.clear();
      userList.innerHTML = `
        <input class="form-check-input user-group-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}">
        <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
        <label class="form-check-label" for='user${user.id}'>${user.username}</label>
      `;
      searchInput.value = '';
    });
  });
});

// スケジュール登録(ユーザ選択)
document.addEventListener('DOMContentLoaded', function () {
  console.log('スケジュール登録(スケジュール詳細画面)していくよー')

  const selectedUsersDisplay = document.getElementById('selectedUsersDisplay');
  const selectedUsersInput = document.getElementById('selectedUsers');
  const confirmUserSelectionButton = document.getElementById('confirmUserSelection');

  confirmUserSelectionButton.addEventListener('click', () => {
    console.log("追加（登録）ボタンが押されました");

    const selectedUserIds = [];
    const selectedUsernames = [];
    document.querySelectorAll('.user-checkbox:checked').forEach((checkbox) => {
        selectedUserIds.push(parseInt(checkbox.value, 10));
        selectedUsernames.push(checkbox.getAttribute('data-name'));
    });

    console.log("選択したユーザID:", selectedUserIds);
    console.log("選択したユーザ名:", selectedUsernames);

    // 選択したユーザをフォームに反映
    if (selectedUsernames.length > 0) {
        selectedUsersDisplay.innerHTML = selectedUsernames
            .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
            .join('');

        // hidden input に選択したユーザのIDをセット
        selectedUsersInput.value = selectedUserIds.join(',');
        console.log("Hidden Input Value:", selectedUsersInput.value);
    } else {
        selectedUsersDisplay.innerHTML = '<p>ユーザが選択されていません</p>';
        selectedUsersInput.value = "";
    }

    // ユーザ選択モーダルを閉じる
    const userModalElement = document.getElementById('addUserModal');
    const userModal = bootstrap.Modal.getInstance(userModalElement);
    if (userModal) {
        userModal.hide();
    }
  });
});

// スケジュール編集
document.addEventListener('DOMContentLoaded', function () {
  console.log('スケジュール編集していくよー')

  document.querySelectorAll('.edit-btn').forEach((button) => {
    button.addEventListener('click', function () {
      let schedulePk = this.getAttribute('data-pk');
      console.log('編集対象のスケジュールPK:', schedulePk);

      let editForm = document.getElementById('scheduleEditForm');
      editForm.action = `/schedules/schedule_edit/${schedulePk}`;

      document.getElementById('editTask').value = this.closest('tr').querySelector('td:nth-child(2)').textContent.trim();
      document.getElementById('editPlace').value = this.closest('tr').querySelector('td:nth-child(3)').textContent.trim();

      let scheduleUpdateDisplay = document.getElementById('scheduleUpdateDisplay');
      scheduleUpdateDisplay.innerHTML = '<p class="text-center">履歴を取得中...</div>';

      fetch(`/schedules/schedule_history/${schedulePk}`)
        .then(response => response.json())
        .then(data => {
          if (data.success && data.history.length > 0) {
            scheduleUpdateDisplay.innerHTML = data.history
              .map(entry => `<p class="text-center pt-2">${entry.user}さんが${entry.updated_at}に更新しました。</p>`)
              .join('');
          } else {
            scheduleUpdateDisplay.innerHTML = `<p class="text-center">現在、更新履歴はありません。</p>`;
          }
        })
        .catch(error => {
          console.error('履歴の取得に失敗:', error);
          scheduleUpdateDisplay.innerHTML = `<p class="text-center">履歴の取得に失敗しました。</p>`
        });
    });
  });

  document.querySelectorAll('.delete-btn').forEach((button) => {
    button.addEventListener('click', function () {
      let schedulePk = this.getAttribute('data-pk');
      console.log('削除対象のスケジュールPK:', schedulePk);

      let deleteForm = document.getElementById('scheduleDeleteForm');
      deleteForm.action = `/schedules/schedule_delete/${schedulePk}`;
    });
  });
});

// スケジュール編集(ユーザ選択)
document.addEventListener('DOMContentLoaded', function () {

  const selectedUsersDisplay = document.getElementById('selectedEditUsersDisplay');
  const selectedUsersInput = document.getElementById('selectedEditUsers');
  const confirmUserSelectionButton = document.getElementById('confirmEditUserSelection');

  confirmUserSelectionButton.addEventListener('click', () => {
    console.log("追加（登録）ボタンが押されました");

    const selectedUserIds = [];
    const selectedUsernames = [];
    document.querySelectorAll('.user-edit-checkbox:checked').forEach((checkbox) => {
        selectedUserIds.push(parseInt(checkbox.value, 10));
        selectedUsernames.push(checkbox.getAttribute('data-name'));
    });

    console.log("選択したユーザID:", selectedUserIds);
    console.log("選択したユーザ名:", selectedUsernames);

    // 選択したユーザをフォームに反映
    if (selectedUsernames.length > 0) {
        selectedUsersDisplay.innerHTML = selectedUsernames
            .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
            .join('');

        // hidden input に選択したユーザのIDをセット
        selectedUsersInput.value = selectedUserIds.join(',');
        console.log("Hidden Input Value:", selectedUsersInput.value);
    } else {
        selectedUsersDisplay.innerHTML = '<p>ユーザが選択されていません</p>';
        selectedUsersInput.value = "";
    }

    // ユーザ選択モーダルを閉じる
    const userModalElement = document.getElementById('editUserModal');
    const userModal = bootstrap.Modal.getInstance(userModalElement);
    if (userModal) {
        userModal.hide();
    }
  });
});

// Todoリスト
document.getElementById('todoListForm').addEventListener('submit', function (e) {
  console.log('ToDo読み込み完了')

  e.preventDefault();
  const formData = new FormData(this);

  fetch(addToDoUrl, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
    },
  })

  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log("ToDOリスト追加成功:", data.task, "優先度:", data.priority);

      // モーダル閉じる
      const modalElement = document.getElementById('addTodoModal')
      const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
      modal.hide();

      // 新しいタスクをリストに追加
      const newTodo = document.createElement('li');

      // 優先度ごとのクラスを適用
      if (data.priority == "重") {
        newTodo.className = 'list-group-item priority-high';
      } else if (data.priority == "中") {
        newTodo.className = 'list-group-item priority-middle';
      } else {
        newTodo.className = 'list-group-item';
      }

      // チェックボックス追加
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.className = 'todo-checkbox me-2';
      checkbox.dataset.todoId = data.todo_id;
      
      // タスクテキスト作成
      const text = document.createTextNode(`${data.task}(期限：${data.due_date})`);

      // 要素組み合わせ
      newTodo.appendChild(checkbox);
      newTodo.appendChild(text);

      //Todoリスト追加 
      document.querySelector('.list-group').appendChild(newTodo);

      checkbox.addEventListener('change', function () {
        if (this.checked) {
          completeTodo(this.dataset.todoId, newTodo);
        }

      });
    } else {
      console.error(data.errors);
    }
  })
  .catch(error => console.error('Error:', error));
});

// Todo達成
document.addEventListener('DOMContentLoaded', () => {

  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + 1;

  document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function () {
      if (this.checked) {
        const todoId = this.dataset.todoId;
         fetch(`/schedules/schedule/${year}/${month}/complete_todo/${todoId}`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type':'application/json',
          },
          body: JSON.stringify({})
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          if (data.success) {
            this.closest('.list-group-item').remove();
          }
        })
        .catch(error => console.error('Error:', error));
      }
    });
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(',');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function completeTodo(todoId, todoElement) {
  fetch(`/schedules/schedule/${year}/${month}/complete_todo/${todoId}`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      todoElement.remove();
    }
  })
  .catch(error => console.error('Error', error));
}

// 目標編集
document.addEventListener('DOMContentLoaded', function () {
  console.log('目標編集機能読み込み完了');

  // 目標編集フォームの取得
  const editObjectiveForm = document.getElementById('objectiveEditForm');

  document.getElementById('objectiveEditForm').addEventListener('submit', function (e) {
      e.preventDefault();  // フォームのデフォルト送信を防ぐ

      console.log("目標編集を送信開始");

      const formData = new FormData(this);

      fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
              'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
          },
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              console.log("目標編集成功:", data.objective);

              // 目標をページに反映（既存の h2 タグを更新）
              const objectiveElement = document.querySelector('.objective-item');
              if (objectiveElement) {
                  objectiveElement.textContent = data.objective;
              }

              // モーダルを閉じる
              const modal = bootstrap.Modal.getInstance(document.getElementById('editObjectiveModal'));
              if (modal) {
                  modal.hide();
              }

              // ページをリダイレクト（オプション）
              window.location.href = data.redirect_url;

          } else {
              console.error("目標編集エラー:", data.errors);
          }
      })
      .catch(error => console.error("通信エラー:", error));
  });
});

// 目標設定
document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('objectiveRegistForm').addEventListener('submit', function (e) {
    console.log('目標設定')

    e.preventDefault();
    const formData = new FormData(this);

    fetch(this.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // モーダル閉じる
        const modal = bootstrap.Modal.getInstance(document.getElementById('addObjectiveModal'));
        modal.hide();

        // 新しい目標をを追加
        const newObjective = document.createElement('h3');
        newObjective.className = 'objective-item';
        newObjective.textContent = `${data.objective}`;
        document.querySelector('.objective-group').appendChild(newObjective);

        console.log("リダイレクトURL:", data.redirect_url);
        window.location.href = data.redirect_url;

      } else {
        console.error("エラー", data.errors)
      }
    })
    .catch(error => console.error("通信エラー", error));
  });
});
