// グローバル定義
window.year = new Date().getFullYear();
window.month = new Date().getMonth() + 1;

// クッキー取得
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

// チャットに新しいメッセージが追加されたらスクロールを一番下に移動
document.addEventListener('DOMContentLoaded', () => {
  const chatBox = document.getElementById('messages');
  chatBox.scrollTop = chatBox.scrollHeight;
});

// ブラウザ通知設定
document.addEventListener('DOMContentLoaded', function () {
  const enableBtn = document.getElementById('enableNotifications');
  const disableBtn = document.getElementById('disableNotifications');
  const enableModalBtn = document.getElementById('enableModal');

  const NOTIFICATION_KEY = 'notificationEnabled';

  // 通知ボタンの表示切替
  console.log(Notification.permission);
  if (Notification.permission === 'granted' && localStorage.getItem(NOTIFICATION_KEY) === 'true') {
    disableBtn.style.display = 'block';
    enableModalBtn.style.display = 'none';
    console.log('通知前準備')
    fetch('/accounts/user/notification_data')
      .then(response => {
        if (!response.ok) {
          throw new Error('データ取得失敗');
        }
        console.log('レスポンス受信')
        return response.json();
      })
      .then(data => {
        if (data.notification) {
          console.log('通知準備')
          // スケジュールメッセージ
          let sch_message = '';
          if (data.schedules.length > 0) {
            data.schedules.forEach(schedule => {
              sch_message += `${schedule}\n`;
            })
          } else {
            sch_message += 'なし\n';
          }
          
          // タスクメッセージ
          let tsk_message = '';
          if (data.tasks > 0) {
            tsk_message += `残りのタスク${data.tasks}個\n`;
          } else {
            tsk_message = '';
          }
          let tsk_tdy_message = '';
          if (data.tasks_today > 0) {
            tsk_tdy_message += `本日期限のタスクは${data.tasks_today}個\n`;
          } else {
            tsk_tdy_message = '';
          }

          // 目標メッセージ
          let obj_message = '';
          if (data.due_days > 0) {
            obj_message += `目標達成まであと${data.due_days}日!\n達成に向けてコツコツ取り組もう!!`
          } else if (data.due_days < 0) {
            obj_message += '目標の達成期限が過ぎています！\n最後までやり切ろう!!';
          } else if (data.due_days === 0) {
            obj_message += '本日目標達成期日です!\nラストスパート!!';
          } else {
            obj_message = '';
          }

          // 通知：スケジュール(5秒後)
          setTimeout(() => {
            new Notification('本日の予定', {
              body: '本日の予定：' + sch_message,
              icon: '/static/generals/notification-icon.png'
            });
          }, 5000);

          // 通知：タスク
          if (tsk_message != '' && tsk_tdy_message != '') {
            setTimeout(() => {
              new Notification('残りのタスク', {
                body: tsk_message + tsk_tdy_message + 'タスクを倒してランクアップしよう!!',
                icon: '/static/generals/notification-icon.png'
              });
            }, 6000);
          };

          // 通知：目標
          if (obj_message != '') {
            setTimeout(() => {
              new Notification('目標カウントダウン', {
                body: obj_message,
                icon: '/static/generals/notification-icon.png'
              });
            }, 7000);
          };

          console.log('これからnotificationを変更していく')
          // notificationをFalseにする
          fetch('/accounts/user/mark_notification_sent', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
          }).then(res => {
            if (res.ok) console.log('通知済みとしてマークしました');
          });
        }
      })
  
  } else {
    enableModalBtn.style.display = 'block';
    disableBtn.style.display = 'none';
  }

  // 通知有効化
  enableBtn.addEventListener('click', () => {
    // モーダルを閉じる
    const confirmModalElement = document.getElementById('confirmEnableModal')
    const confirmModal = bootstrap.Modal.getInstance(confirmModalElement);
    if (confirmModal) {
        confirmModal.hide();
    }
    
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        localStorage.setItem(NOTIFICATION_KEY, 'true');
        disableBtn.style.display = 'block';
        enableModalBtn.style.display = 'none';
      } else {
        console.log('通知が拒否されました');
      }
    });
  });

  // 通知無効化
  disableBtn.addEventListener('click', () => {
    localStorage.removeItem(NOTIFICATION_KEY);
    enableModalBtn.style.display = 'block';
    disableBtn.style.display = 'none';
  });
});

// 質問テンプレート
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
// テンプレート挿入
function insertTemplate(templateId){
  const templateElement = document.getElementById(templateId);
  const templateText = templateElement.innerText || templateElement.textContent;

  const commentField = document.getElementById('comment-field');
  commentField.value = templateText;
} 

// 回答フォーム展開
document.addEventListener("DOMContentLoaded", function () {
  const answerButton = document.getElementById("answer-btn");
  const answerFormContainer = document.getElementById("answer-form-container");

  answerButton.addEventListener("click", function () {
    if (answerFormContainer.style.display === "none" || answerFormContainer.style.display === "") {
      answerFormContainer.style.display = "block";
      answerButton.textContent = '戻る';
    } else {
      answerFormContainer.style.display = "none";
      answerButton.textContent = '回答する';
    }
  });
});

// 回答編集・削除
document.addEventListener('DOMContentLoaded', function () {
  const answerEditButton = document.getElementById("answer-edit-btn");
  const answerCard = document.getElementById('answer-card');

  // 編集
  answerEditButton.addEventListener('click', function () {
    const answerId = this.dataset.answerId;
    console.log('取得回答ID：', answerId);

    // 編集フォーム表示
    const answerEditFormContainer = document.getElementById("answer-editForm-container");
    if (answerEditFormContainer.style.display === 'none' || answerEditFormContainer.style.display === '') {
      answerEditFormContainer.style.display = 'block';
      answerCard.style.display = 'none';
      answerEditButton.textContent = '戻る';

      const answerEditForm = document.getElementById('answerEditForm')
      answerEditForm.action = `/questions/answer_edit/${answerId}`;

      fetch(`/questions/get_answer_data/${answerId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('answerComment').value = data.comment;
            if (data.picture) {
              document.getElementById('answerPicture').src = data.picture;
            }
        });
    } else {
      answerEditFormContainer.style.display = 'none';
      answerCard.style.display = 'block';
      answerEditButton.textContent = '編集';
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
        searchInput.value = '';
      });
  });
});

// チャットグループ(ユーザ選択)
document.addEventListener('DOMContentLoaded', function () {
  const selectedUsersDisplay = document.getElementById('selectedGroupUsersDisplay');
  const selectedUsersInput = document.getElementById('selectedGroupUsers');
  const confirmUserSelectionButton = document.getElementById('addGroupUsers');
  const pageErrorContainer = document.getElementById('chatgroupFormErrors');
  const pageSuccessContainer = document.getElementById('FormSuccess');

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
    // デフォルトメッセージ削除
    document.getElementById('default-message').innerHTML = '';
  });

  // チャットグループ登録
  let chatGroupForm = document.getElementById('chatgroupForm');
  chatGroupForm.action = `/chats/chat/chatsgroup_create/`;

  chatGroupForm.addEventListener('submit', function (e) {
    e.preventDefault()
    pageErrorContainer.innerHTML = '';

    const formData = new FormData(chatGroupForm);

    fetch(chatGroupForm.action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          // モーダル閉じる
          const modal = bootstrap.Modal.getInstance(document.getElementById('addChatGroupModal'));
          modal.hide();

          // ページリロード
          location.reload();

        } else if (data.status === 'error') {
          console.error("エラー", data.errors)

          // エラーメッセージ表示
          pageErrorContainer.innerHTML = '';

          const wrapper = document.createElement('div');
          wrapper.className = 'alert alert-danger';

          const title = document.createElement('div');
          title.textContent = 'チャットグループに失敗しました。以下をご確認ください。';
          wrapper.appendChild(title);

          for (const label in data.errors) {
            data.errors[label].forEach(errorMsg => {
              const errorLine = document.createElement('li');
              errorLine.textContent = `${label}: ${errorMsg}`;
              wrapper.appendChild(errorLine);
            });
          }

          pageErrorContainer.appendChild(wrapper);
        }
      })
      .catch(err => {
      console.log('通信エラー：', err);
    });
  })
});

// チャットグループ編集
document.addEventListener('DOMContentLoaded', function () {
  const chatgroupEditUserDisplay = document.getElementById('editGroupUsersDisplay')
  const chatgroupEditUserInput = document.getElementById('chatgroupEditSelectedUsers')
  const pageErrorContainer = document.getElementById('chatgroupEditFormErrors');
  const pageSuccessContainer = document.getElementById('FormSuccess');

  document.querySelectorAll('.edit-chatgroup-btn').forEach((button) => {
    button.addEventListener('click', function () {
      pageErrorContainer.innerHTML = '';
      let chatgroupPk = this.getAttribute('chatgroup-data-pk');
      console.log('編集対象のチャットグループPK:', chatgroupPk);

      let editForm = document.getElementById('chatgroupEditForm');
      editForm.action = `/chats/chat/chatsgroup_edit/${chatgroupPk}`;

      // ユーザー情報を取得しておく（グローバルに保存など）
      fetch(`/chats/chat/get_chatgroup_data/${chatgroupPk}`)
        .then(response => response.json())
        .then(data => {
          document.getElementById('editGroupname').value = data.groupname;

          const ChatgroupEditSelectedUserIds = []
          const ChatgroupEditSelectedUserNames = []
          ChatgroupEditSelectedUserIds.push(...data.user_ids);
          ChatgroupEditSelectedUserNames.push(...data.usernames);
          console.log('取得したユーザーid：', ChatgroupEditSelectedUserIds);
          console.log('取得したユーザー名：', ChatgroupEditSelectedUserNames);
          
          // 既存データ反映
          if (ChatgroupEditSelectedUserNames.length > 0) {
            console.log('既に登録されているユーザー名表示', ChatgroupEditSelectedUserNames);
            chatgroupEditUserDisplay.innerHTML = ChatgroupEditSelectedUserNames
              .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
              .join('');
            
            console.log('既に登録されているユーザーidを渡す', ChatgroupEditSelectedUserIds)
            ChatgroupEditSelectedUserIds.forEach(id => {
              const input = document.createElement('input');
              input.type = 'hidden';
              input.name = 'chatgroup_user';
              input.value = id;
              chatgroupEditUserInput.append(input);
              console.log(chatgroupEditUserInput)
            });
          } else {
            chatgroupEditUserDisplay.innerHTML = '<p>ユーザーが選択されていません</p>';
            chatgroupEditUserInput.value = '';
          }
        });
      
      editForm.addEventListener('submit', function (e) {
        e.preventDefault()
        pageErrorContainer.innerHTML = '';

        const formData = new FormData(editForm);

        fetch(editForm.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: formData
        })
          .then(res => res.json())
          .then(data => {
            if (data.status === 'success') {
              // モーダル閉じる
              const modal = bootstrap.Modal.getInstance(document.getElementById('editChatGroupModal'));
              modal.hide();

              // ページリロード
              location.reload();
            } else if (data.status === 'error') {
              console.error("エラー", data.errors)

              // エラーメッセージ表示
              pageErrorContainer.innerHTML = '';

              const wrapper = document.createElement('div');
              wrapper.className = 'alert alert-danger';

              const title = document.createElement('div');
              title.textContent = 'チャットグループ編集に失敗しました。以下をご確認ください。';
              wrapper.appendChild(title);

              for (const label in data.errors) {
                data.errors[label].forEach(errorMsg => {
                  const errorLine = document.createElement('li');
                  errorLine.textContent = `${label}: ${errorMsg}`;
                  wrapper.appendChild(errorLine);
                });
              }

              pageErrorContainer.appendChild(wrapper);
            }
          })
          .catch(err => {
          console.log('通信エラー：', err);
        });
      })
    });
  });

  // チャットグループ削除
  document.querySelectorAll('.delete-chatgroup-btn').forEach((button) => {
    console.log('グループ削除読み込み')
    button.addEventListener('click', function () {
      let chatgroupPk = this.getAttribute('chatgroup-data-pk');
      console.log('削除対象のチャットグループPK:', chatgroupPk);

      let deleteForm = document.getElementById('chatgroupDeleteForm');
      deleteForm.action = `/chats/chat/chatsgroup_delete/${chatgroupPk}`;
    });
  });
});

// モーダル内ユーザ検索機能(チャットグループ編集)
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.chatgroup-edit-selectuser-modal').forEach(modal => {
    const searchForm = document.getElementById('chatgroupEditSelectSearchForm');
    const searchInput = document.getElementById('chatgroupEditSelectSearchInput');
    const userList = document.getElementById('chatgroupEditSelectUserList');

    let chatgroupSelectedUsers = new Set();
  
    searchForm.addEventListener('submit', function(event) {
      event.preventDefault();

      const chatgroupSearchQuery = searchInput.value;

      fetch(`/chats/chat/search_users?search=${encodeURIComponent(chatgroupSearchQuery)}`)
        .then(response => response.json())
        .then(data => {

          modal.querySelectorAll('.chatgroup-user-edit-checkbox').forEach(checkbox => {
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
                <input class="form-check-input chatgroup-user-edit-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}" ${isChecked}>
                <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
                <label class="form-check-label" for='user${user.id}'>${user.username}</label>
            `
            userList.appendChild(userDiv);
          });

          modal.querySelectorAll('.chatgroup-user-edit-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
              if (this.checked) {
                chatgroupSelectedUsers.add(this.value);
              } else {
                chatgroupSelectedUsers.delete(this.value);
              }
            });
          });

          // モーダルが閉じられた時にデータをリセット
          modal.addEventListener('hidden.bs.modal', function () {
            chatgroupSelectedUsers.clear();
            searchInput.value = '';
          });
        })
        .catch(error => console.error('Error:', error));
    });
  });
});

// チャットグループ編集(ユーザー選択)
document.addEventListener('DOMContentLoaded', function () {
  const chatgroupEditSelectedUserDisplay = document.getElementById('editGroupUsersDisplay');
  const chatgroupEditSelectedUserButton = document.getElementById('editChatgroupUsers');
  const chatgroupEditSelectedUserInput = document.getElementById('chatgroupEditSelectedUsers');

  chatgroupEditSelectedUserButton.addEventListener('click', () => {
    newChatgroupEditSelectedUserIds = []
    newChatgroupEditSelectedUserNames = []
    const checkedCheckboxes = document.querySelectorAll('.chatgroup-user-edit-checkbox:checked');

    checkedCheckboxes.forEach((checkbox) => {
      const userId = parseInt(checkbox.value, 10);
      const username = checkbox.getAttribute('data-name');

      newChatgroupEditSelectedUserIds.push(userId);
      newChatgroupEditSelectedUserNames.push(username);
    });

    console.log('現在のユーザーID：', newChatgroupEditSelectedUserIds);
    console.log('現在のユーザー名：', newChatgroupEditSelectedUserNames);

    // ユーザー名表示
    if (newChatgroupEditSelectedUserNames.length > 0) {
      console.log('新しく追加したユーザー名表示：', newChatgroupEditSelectedUserNames);
      chatgroupEditSelectedUserDisplay.innerHTML = newChatgroupEditSelectedUserNames
        .map(name => `<span class="badge bg-primary me-1">${name}</span>`)
        .join('');

      chatgroupEditSelectedUserInput.innerHTML = '';
      // hidden input に選択したユーザーidセット
      console.log('新しく追加したユーザーid:', newChatgroupEditSelectedUserIds)
      newChatgroupEditSelectedUserIds.forEach(id => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'chatgroup_user';
        input.value = id;
        chatgroupEditSelectedUserInput.append(input);
        console.log('input要素：', chatgroupEditSelectedUserInput);
      });
    } else {
      chatgroupEditSelectedUserDisplay.innerHTML = `<p>ユーザーが選択されていません</p>`
    }

    // ユーザ選択モーダルを閉じる
    const editChatgroupUserModalElement = document.getElementById('editChatgroupUserModal');
    const editChatgroupUserModal = bootstrap.Modal.getInstance(editChatgroupUserModalElement);
    if (editChatgroupUserModal) {
      editChatgroupUserModal.hide();
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
      searchInput.value = '';
    });
  });
});

// スケジュール登録(ユーザ選択)
document.addEventListener('DOMContentLoaded', function () {
  console.log('スケジュール登録(スケジュール詳細画面)していくよー')

  const selectedUsersDisplay = document.getElementById('selectedUsersDisplay');
  const selectedUsersInput = document.getElementById('scheduleSelectedUserInput');
  const confirmUserSelectionButton = document.getElementById('confirmUserSelection');

  confirmUserSelectionButton.addEventListener('click', () => {
    console.log("追加（登録）ボタンが押されました");

    const selectedUserIds = [];
    const selectedUsernames = [];
    const checkedCheckboxes = document.querySelectorAll('.user-checkbox:checked');
    checkedCheckboxes.forEach((checkbox) => {
      const userId = parseInt(checkbox.value, 10);
      const username = checkbox.getAttribute('data-name');
      selectedUserIds.push(userId);
      selectedUsernames.push(username);
    });

    console.log("選択したユーザID:", selectedUserIds);
    console.log("選択したユーザ名:", selectedUsernames);

    // 選択したユーザをフォームに反映
    if (selectedUsernames.length > 0) {
        selectedUsersDisplay.innerHTML = selectedUsernames
          .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
          .join('');

        // hidden input に選択したユーザのIDをセット
        selectedUsersInput.innerHTML = '';

        selectedUserIds.forEach(id => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'schedule_user';
          input.value = id;
          selectedUsersInput.append(input);
        })
        console.log('ユーザーを追加しました：', selectedUsersInput);
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
    // デフォルトメッセージ削除
    document.getElementById('default-message').innerHTML = '';
  });

  // スケジュール登録(スケジュールからの登録)
  const pageErrorContainer = document.getElementById('scheduleFormErrors');
  const pageSuccessContainer = document.getElementById('FormSuccess');

  let scheduleRegistForm = document.getElementById('scheduleForm');
  scheduleRegistForm.action = `/schedules/schedule_regist`;

  scheduleRegistForm.addEventListener('submit', function (e) {
    e.preventDefault()
    pageErrorContainer.innerHTML = '';

    const formData = new FormData(scheduleRegistForm);

    fetch(scheduleRegistForm.action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          // モーダル閉じる
          const modal = bootstrap.Modal.getInstance(document.getElementById('addScheduleModal'));
          modal.hide();

          // 成功メッセージ
          localStorage.setItem('successText', 'スケジュールを登録しました。');

          // ページリロード
          location.reload();
        } else if (data.status === 'error') {
          console.error("エラー", data.errors)

          // エラーメッセージ表示
          pageErrorContainer.innerHTML = '';

          const wrapper = document.createElement('div');
          wrapper.className = 'alert alert-danger';

          const title = document.createElement('div');
          title.textContent = 'スケジュール登録に失敗しました。以下をご確認ください。';
          wrapper.appendChild(title);

          for (const label in data.errors) {
            data.errors[label].forEach(errorMsg => {
              const errorLine = document.createElement('li');
              errorLine.textContent = `${label}: ${errorMsg}`;
              wrapper.appendChild(errorLine);
            });
          }

          pageErrorContainer.appendChild(wrapper);
        }
      })
      .catch(err => {
      console.log('通信エラー：', err);
    });
  });
});

// 時刻表示変換(UTC → JST)
function setDatetimeLocal(inputId, utcString) {
  const date = new Date(utcString);
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());

  const formatted = date.toISOString().slice(0, 16);
  document.getElementById(inputId).value = formatted;
}

// スケジュール登録(チャットからの登録)
document.addEventListener('DOMContentLoaded', function () {
  console.log('チャットからスケジュール登録')
  // 取得したチャットグループのユーザーを対象にデフォルトで値をセット
  const chatgroupScheduleUserDisplay = document.getElementById('chatgroupSelectedUsersDisplay');
  const chatgorupScheduleUserInput = document.getElementById('chatgroupScheduleUsersInput');
  const pageErrorContainer = document.getElementById('chatScheduleFormErrors');
  const pageSuccessContainer = document.getElementById('FormSuccess');

  document.querySelectorAll('.group-schedule-rgsbtn').forEach((button) => {
    button.addEventListener('click', function () {
      pageErrorContainer.innerHTML = '';
      let chatgroupPk = this.getAttribute('data-pk');
      console.log('スケジュール登録対象グループPK：', chatgroupPk);

      let scheduleRegistForm = document.getElementById('scheduleListForm');
      scheduleRegistForm.action = `/schedules/schedule_regist`;

      fetch(`/chats/chat/get_chatgroup_data/${chatgroupPk}`)
        .then(response => response.json())
        .then(data => {
          const ChatgroupScheduleSelectedUserIds = []
          const ChatgroupScheduleSelectedUserNames = []
          ChatgroupScheduleSelectedUserIds.push(...data.user_ids);
          ChatgroupScheduleSelectedUserNames.push(...data.usernames);
          console.log('取得したユーザーid：', ChatgroupScheduleSelectedUserIds);
          console.log('取得したユーザー名：', ChatgroupScheduleSelectedUserNames);

          // グループメンバーをデフォルト設置
          if (chatgroupPk == 1) {
            chatgroupScheduleUserDisplay.innerHTML = '全ユーザーに登録されます';
          } else {
            chatgroupScheduleUserDisplay.innerHTML = ChatgroupScheduleSelectedUserNames
              .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
              .join('');
          }

          // Idを渡す
          ChatgroupScheduleSelectedUserIds.forEach(id => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'schedule_user';
            input.value = id;
            chatgorupScheduleUserInput.append(input);
            console.log(chatgorupScheduleUserInput);
          });
        })

      scheduleRegistForm.addEventListener('submit', function (e) {
        e.preventDefault()
        pageErrorContainer.innerHTML = '';

        const formData = new FormData(scheduleRegistForm);

        fetch(scheduleRegistForm.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: formData
        })
          .then(res => res.json())
          .then(data => {
            if (data.status === 'success') {
              // モーダル閉じる
              const modal = bootstrap.Modal.getInstance(document.getElementById('addScheduleModal'));
              modal.hide();

              // 成功メッセージ
              localStorage.setItem('successText', 'スケジュールを登録しました。スケジュール画面のカレンダーをご確認ください。');

              // ページリロード
              location.reload();

            } else if (data.status === 'error') {
              console.error("エラー", data.errors)

              // エラーメッセージ表示
              pageErrorContainer.innerHTML = '';

              const wrapper = document.createElement('div');
              wrapper.className = 'alert alert-danger';

              const title = document.createElement('div');
              title.textContent = 'スケジュール登録に失敗しました。以下をご確認ください。';
              wrapper.appendChild(title);

              for (const label in data.errors) {
                data.errors[label].forEach(errorMsg => {
                  const errorLine = document.createElement('li');
                  errorLine.textContent = `${label}: ${errorMsg}`;
                  wrapper.appendChild(errorLine);
                });
              }

              pageErrorContainer.appendChild(wrapper);
            }
          })
          .catch(err => {
          console.log('通信エラー：', err);
        });
      });
    });
  });
});

// スケジュール編集
document.addEventListener('DOMContentLoaded', function () {
  const pageErrorContainer = document.getElementById('chatScheduleEditFormErrors');

  document.querySelectorAll('.edit-btn').forEach((button) => {
    button.addEventListener('click', function () {
      console.log('スケジュール編集ボタンが押下されました');
      pageErrorContainer.innerHTML = '';
      const scheduleEditUserDisplay = document.getElementById('selectedEditUsersDisplay');
      const scheduleEditUserInput = document.getElementById('scheduleEditSelectedUsers');

      let schedulePk = this.getAttribute('data-pk');
      console.log('編集対象のスケジュールPK:', schedulePk);

      let editForm = document.getElementById('scheduleEditForm');
      const childEditForm = document.getElementById('editForm');
      editForm.appendChild(childEditForm);
      editForm.action = `/schedules/schedule_edit/${schedulePk}`;

      document.getElementById('editTask').value = this.closest('tr').querySelector('td:nth-child(2)').textContent.trim();
      document.getElementById('editPlace').value = this.closest('tr').querySelector('td:nth-child(3)').textContent.trim().replace(/@/, '');

      scheduleEditUserInput.innerHTML = '';
      // ユーザー情報を取得しておく（グローバルに保存など）
      fetch(`/schedules/schedule_show/get_schedule_data/${schedulePk}`)
        .then(response => response.json())
        .then(data => {
          // スケジュール開始・終了時間を表示
          setDatetimeLocal('ScheduleStartAt', data.start_at);
          setDatetimeLocal('ScheduleEndAt', data.end_at);

          const ScheduleEditSelectedUserIds = []
          const ScheduleEditSelectedUserNames = []
          ScheduleEditSelectedUserIds.push(...data.user_ids);
          ScheduleEditSelectedUserNames.push(...data.usernames);
          console.log('取得したユーザーid：', ScheduleEditSelectedUserIds);
          console.log('取得したユーザー名：', ScheduleEditSelectedUserNames);

          // 既存データ反映
          if (ScheduleEditSelectedUserNames.length > 0) {
            scheduleEditUserDisplay.innerHTML = '';
            console.log('既に登録されているユーザー名表示：', ScheduleEditSelectedUserNames);
            scheduleEditUserDisplay.innerHTML = ScheduleEditSelectedUserNames
              .map(username => `<span class="badge bg-primary me-1">${username}</span>`)
              .join('');
            
            console.log('既に登録されているユーザーidを渡す', ScheduleEditSelectedUserIds);
            ScheduleEditSelectedUserIds.forEach(id => {
              const input = document.createElement('input');
              input.type = 'hidden';
              input.name = 'edit_user';
              input.value = id;
              scheduleEditUserInput.append(input);
            });
          } else {
            scheduleEditUserDisplay.innerHTML = '<p>ユーザーが選択されていません</p>';
          }
        });
      
      editForm.addEventListener('submit', function (e) {
        e.preventDefault();
        pageErrorContainer.innerHTML = '';

        const formData = new FormData(editForm);

        fetch(editForm.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: formData
        })
          .then(res => res.json())
          .then(data => {
             if (data.status === 'success') {
              // モーダル閉じる
              const modal = bootstrap.Modal.getInstance(document.getElementById('editScheduleModal'));
              modal.hide();

              // ページリロード
              location.reload();
            } else if (data.status === 'error') {
              console.error("エラー", data.errors)

              // エラーメッセージ表示
              pageErrorContainer.innerHTML = '';

              const wrapper = document.createElement('div');
              wrapper.className = 'alert alert-danger';

              const title = document.createElement('div');
              title.textContent = 'スケジュール編集に失敗しました。以下をご確認ください。';
              wrapper.appendChild(title);

              for (const label in data.errors) {
                data.errors[label].forEach(errorMsg => {
                  const errorLine = document.createElement('li');
                  errorLine.textContent = `${label}: ${errorMsg}`;
                  wrapper.appendChild(errorLine);
                });
              }

              pageErrorContainer.appendChild(wrapper);
            }
          })
          .catch(err => {
          console.log('通信エラー：', err);
        });
      })

      // 編集履歴
      let scheduleUpdateDisplay = document.getElementById('scheduleUpdateDisplay');
      scheduleUpdateDisplay.innerHTML = '<p class="text-center">履歴を取得中...</div>';

      fetch(`/schedules/schedule_history/${schedulePk}`)
        .then(response => response.json())
        .then(data => {
          if (data.success && data.history.length > 0) {
            scheduleUpdateDisplay.innerHTML = data.history
              .map(entry => {
                // 表示時間をUTC → JSTへ変換
                const date = new Date(entry.updated_at);
                date.setHours(date.getHours() + 9);

                const formatted = date.toLocaleString('ja-JP', {
                  year: 'numeric',
                  month: '2-digit',
                  day: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit'
                });

                return `<p class="text-center pt-2">${entry.user}さんが${formatted}に更新しました。</p>`;
              })
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

// モーダル内ユーザ検索機能(スケジュール編集)
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.schedule-edit-selectuser-modal').forEach(modal => {
    const searchForm = document.getElementById('scheduleEditSelectSearchForm');
    const searchInput = document.getElementById('scheduleEditSelectSearchInput');
    const userList = document.getElementById('scheduleEditSelectUserList');

    let scheduleSelectedUsers = new Set();

    searchForm.addEventListener('submit', function(event) {
      event.preventDefault();

      const scheduleSearchQuery = searchInput.value;

      fetch(`/schedules/schedule_show/search_users?search=${encodeURIComponent(scheduleSearchQuery)}`)
        .then(response => response.json())
        .then(data => {

          modal.querySelectorAll('.user-edit-checkbox').forEach(checkbox => {
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

            const isChecked =  scheduleSelectedUsers.has(user.id) ? 'checked' : '';

            userDiv.innerHTML = `
                <input class="form-check-input user-edit-checkbox" type="checkbox" value="${user.id}" id='user${user.id}' data-name="${user.username}" ${isChecked}>
                <img class="profile-icon rounded-circle" id="profile-icon" src="${user.picture}" alt="Profile Icon" style="width: 30px; height: 30px; object-fit: cover;">
                <label class="form-check-label" for='user${user.id}'>${user.username}</label>
            `
            userList.appendChild(userDiv);
          });

          modal.querySelectorAll('.user-edit-checkbox').forEach(checkbox => {
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
      searchInput.value = '';
    });
  });
});

// スケジュール編集(ユーザ選択)
document.addEventListener('DOMContentLoaded', function () {
  const scheduleEditSelectedUserDisplay = document.getElementById('selectedEditUsersDisplay');
  const scheduleEditSelectedUserInput = document.getElementById('scheduleEditSelectedUsers');
  const confirmUserSelectionButton = document.getElementById('confirmEditUserSelection');

  confirmUserSelectionButton.addEventListener('click', () => {
    console.log("追加（登録）ボタンが押されました");
    const newScheduleEditSelectedUserIds = [];
    const newScheduleEditSelectedUserNames = [];
    const checkedCheckboxes = document.querySelectorAll('.user-edit-checkbox:checked');
    
    checkedCheckboxes.forEach((checkbox) => {
      const userId = parseInt(checkbox.value, 10);
      const username = checkbox.getAttribute('data-name');
      newScheduleEditSelectedUserIds.push(userId);
      newScheduleEditSelectedUserNames.push(username);
    });

    console.log("選択したユーザID:", newScheduleEditSelectedUserIds);
    console.log("選択したユーザ名:", newScheduleEditSelectedUserNames);

    // ユーザー表示
    if (newScheduleEditSelectedUserNames.length > 0) {
      scheduleEditSelectedUserDisplay.innerHTML = '';
      console.log('新しく追加したユーザー名：', newScheduleEditSelectedUserNames);
      scheduleEditSelectedUserDisplay.innerHTML = newScheduleEditSelectedUserNames
        .map(name => `<span class="badge bg-primary me-1">${name}</span>`)
        .join('');
      
      scheduleEditSelectedUserInput.innerHTML = '';
      // hidden valueに選択したユーザーidをセット
      console.log('新しく追加したユーザーidを渡す：', newScheduleEditSelectedUserIds);
      newScheduleEditSelectedUserIds.forEach(id => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'edit_user';
        input.value = id;
        scheduleEditSelectedUserInput.append(input);
        console.log('input要素：', scheduleEditSelectedUserInput);
      });
    } else {
      scheduleEditSelectedUserDisplay.innerHTML = '<p>ユーザが選択されていません</p>';
      scheduleEditSelectedUserInput.value = '';
    }

    // ユーザ選択モーダルを閉じる
    const userModalElement = document.getElementById('editUserModal');
    const userModal = bootstrap.Modal.getInstance(userModalElement);
    if (userModal) {
        userModal.hide();
    }
    // モーダルを閉じた際に編集ボタンにフォーカスを移す
    document.getElementById('scheduleEditFormButton').focus();
  });
});

// Todoリスト
document.addEventListener('DOMContentLoaded', function () {
  console.log('todo機能が読み込まれました')
  document.getElementById('todoListForm').addEventListener('submit', function (e) {
    console.log('ToDo読み込み完了')

    const pageErrorContainer = document.getElementById('todoFormErrors');
    const pageSuccessContainer = document.getElementById('FormSuccess');
    pageErrorContainer.innerHTML = '';

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

        // フォームはリセット
        document.getElementById('todoListForm').reset();

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

        // 成功メッセージ
        localStorage.setItem('successText', 'ToDoタスクを登録しました。');

        // ページリロード
        location.reload();
      
      } else {
        console.error(data.errors);

        // エラーメッセージ表示
        pageErrorContainer.innerHTML = '';

        const wrapper = document.createElement('div');
        wrapper.className = 'alert alert-danger';

        const title = document.createElement('div');
        title.textContent = 'ToDoタスク登録に失敗しました。以下をご確認ください。';
        wrapper.appendChild(title);

        for (const label in data.errors) {
          data.errors[label].forEach(errorMsg => {
            const errorLine = document.createElement('li');
            errorLine.textContent = `${label}: ${errorMsg}`;
            wrapper.appendChild(errorLine);
          });
        }

        pageErrorContainer.appendChild(wrapper);

      }
    })
    .catch(error => console.error('Error:', error));
  });
});

// Todo達成
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', function () {
      console.log('task達成処理')
      if (this.checked) {
       completeTodo(this.dataset.todoId, this.closest('.list-group-item'));
      }
    });
  });
});

// タスク達成
function completeTodo(todoId, todoElement) {
  console.log('タスク達成処理実行')
  fetch(`/schedules/schedule/${window.year}/${window.month}/complete_todo/${todoId}`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({})
  })
  .then(response => {
    if (!response.ok) throw new Error('通信エラー');
    return response.json();
  })
  .then(data => {
    if (data.success) {
      todoElement.remove();

      // 成功メッセージ
      localStorage.setItem('successText', 'ToDoタスクを完了させました。');

      // ページリロード
      location.reload();

    }
  })
  .catch(error => console.error('Error', error));
}

// 目標設定
document.addEventListener('DOMContentLoaded', function () {
  console.log('目標設定読み込み')
  const pageErrorContainer = document.getElementById('objectiveFormErrors');
  
  document.getElementById('objectiveRegistForm').addEventListener('submit', function (e) {

    e.preventDefault();
    const formData = new FormData(this);
    
    fetch(this.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
      },
    })
    .then(response => {
      if(!response.ok) location.reload();
      return response.json();
    })
    .then(data => {
      console.log('目標登録実施開始')
      if (data.success) {
        // モーダル閉じる
        const modal = bootstrap.Modal.getInstance(document.getElementById('addObjectiveModal'));
        modal.hide();

        // 新しい目標を追加
        const newObjective = document.createElement('h3');
        newObjective.className = 'objective-item';
        console.log(data.objective);
        newObjective.textContent = `${data.objective}`;
        document.querySelector('.objective-group').appendChild(newObjective);

        // ページリロード
        location.reload();

      } else {
        console.error("エラー", data.errors)

        // エラーメッセージ表示
        pageErrorContainer.innerHTML = '';

        const wrapper = document.createElement('div');
        wrapper.className = 'alert alert-danger';

        const title = document.createElement('div');
        title.textContent = '目標設定に失敗しました。以下をご確認ください。';
        wrapper.appendChild(title);

        for (const label in data.errors) {
          data.errors[label].forEach(errorMsg => {
            const errorLine = document.createElement('li');
            errorLine.textContent = `${label}: ${errorMsg}`;
            wrapper.appendChild(errorLine);
          });
        }

        pageErrorContainer.appendChild(wrapper);
      }
    })
    .catch(error => console.error("通信エラー", error));
  });
});

// 目標編集
document.addEventListener('DOMContentLoaded', function () {
  console.log('目標編集機能読み込み完了');
  const pageSuccessContainer = document.getElementById('FormSuccess')
  const pageErrorContainer = document.getElementById('objectiveEditFormErrors');
  const editForm = document.getElementById('objectiveEditForm');

  document.querySelectorAll('.objective-edit-btn').forEach((button) => {
    button.addEventListener('click', function () {
      pageErrorContainer.innerHTML = '';
      let objectivePk = this.getAttribute('objective-data-pk');
      console.log('編集対象：', objectivePk);

      fetch(`/schedules/get_objective_data/${objectivePk}`)
        .then(response => {
          if(!response.ok) throw new Error('データ取得失敗');
          return response.json();
        })
        .then(data => {
          console.log('取得データ：', data)
          document.getElementById('editObjective').value = data.objective;
          const rawDate = data.objective_due_date;
          const isoDate = rawDate.replace(" ", "T") + ":00Z";
          setDatetimeLocal('editObjectiveDueDate', isoDate);
          console.log('受け取ったデータ:', data.objective_due_date);
          console.log('文字列→Date:', new Date(data.objective_due_date));
        })
        .catch(error => {
          console.log('エラー：', error);
        });
      
      editForm.addEventListener('submit', function (e) {
        e.preventDefault();
        pageErrorContainer.innerHTML = '';

        const formData = new FormData(editForm);
          
        editForm.action = `/schedules/objective_edit/${objectivePk}`;
        fetch(editForm.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
          },
          body: formData
        })
        .then(res => res.json())
        .then(data => {
          if(data.status === 'success') {
            // モーダル閉じる
            const modal = bootstrap.Modal.getInstance(document.getElementById('editObjectiveModal'));
            modal.hide();

            location.reload();

          } else if (data.status === 'error') {

            // エラーメッセージ表示
            pageErrorContainer.innerHTML  = '';

            const wrapper = document.createElement('div');
            wrapper.className = 'alert alert-danger';

            const title = document.createElement('div');
            title.textContent = '目標設定に失敗しました。以下をご確認ください。';
            wrapper.appendChild(title);

            for (const label in data.errors) {
              data.errors[label].forEach(errorMsg => {
                const errorLine = document.createElement('li');
                errorLine.textContent = `${label}: ${errorMsg}`;
                wrapper.appendChild(errorLine);
              });
            }

            pageErrorContainer.appendChild(wrapper);
          }
        })
        .catch(err => {
          console.log('通信エラー：', err);
        });
      });
    });
  });
});

// 成功メッセージ表示
document.addEventListener('DOMContentLoaded', function () {
  console.log('成功メッセージを表示します');
  const pageSuccessContainer = document.getElementById('FormSuccess');
  const successText = localStorage.getItem('successText');

  if (successText) {
    const successMsg = document.createElement('div');
    successMsg.className = 'alert alert-info';
    successMsg.textContent = successText;
    pageSuccessContainer.appendChild(successMsg);
    localStorage.removeItem('successText');
  }
})