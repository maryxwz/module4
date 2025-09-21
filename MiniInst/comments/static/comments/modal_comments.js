(function(){
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
  }
  const csrftoken = getCookie('csrftoken');

  async function api(params) {
    const url = "/comments/api/";
    if (params.method === "GET") {
      const q = new URLSearchParams(params.query || {}).toString();
      const resp = await fetch(url + (q ? ("?" + q) : ""), { headers: {"X-Requested-With":"XMLHttpRequest"} });
      return await resp.json();
    } else {
      const body = new URLSearchParams(params.body || {});
      const resp = await fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken, "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
        body
      });
      return await resp.json();
    }
  }

  function showToast(modal, msg, ms=3000){
    const el = modal.querySelector(".cmodal__toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("is-show");
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove("is-show"), ms);
  }

  function escapeHtml(str){
    return String(str ?? "").replace(/[&<>"']/g, s => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[s]));
  }

  function renderList(modal, data) {
    const list = document.createElement("div");
    list.className = "cmodal__list";
    if (!data.comments || data.comments.length === 0) {
      list.innerHTML = `<div class="cmodal__empty">Немає жодного коментаря.</div>`;
    } else {
      list.innerHTML = data.comments.map(c => renderRootItem(c, data.is_auth)).join("");
    }
    const old = modal.querySelector(".cmodal__list");
    if (old) old.remove();
    modal.querySelector(".cmodal__body").appendChild(list);
  }

  function renderRootItem(c, is_auth){
    return `
      <div class="cmtitem" data-cid="${c.id}">
        <div class="cmtitem__avatar">${c.avatar ? `<img src="${c.avatar}">` : `<div class="cmtitem__placeholder">👤</div>`}</div>
        <div class="cmtitem__body">
          <div class="cmtitem__meta">
            <a class="cmtitem__author" href="${c.author_url}" target="_blank">@${escapeHtml(c.author)}</a>
            <span class="cmtitem__date">${escapeHtml(c.created_at)}</span>
            ${c.is_owner ? kebabMenu() : ``}
          </div>
          <div class="cmtitem__text">${escapeHtml(c.text)}</div>

          <div class="replies" data-parent-id="${c.id}">
            <button class="link link--muted" data-toggle-replies>
              ${c.replies_count ? `Показати відповіді (${c.replies_count})` : `Показати відповіді`}
            </button>

            ${is_auth ? `
              <div>
                <button class="link" data-show-reply>Відповісти</button>
                <form class="reply-form" data-reply-parent="${c.id}" hidden>
                  <textarea rows="2" placeholder="Ваша відповідь..."></textarea>
                  <div class="cmtitem__actions">
                    <button class="btn btn--primary" type="submit">Надіслати</button>
                    <button class="btn" type="button" data-hide-reply>Скасувати</button>
                  </div>
                </form>
              </div>
            ` : `<div class="cmodal__hint">Щоб відповісти, увійдіть.</div>`}

            <div class="reply-list" hidden></div>
          </div>
        </div>
      </div>
    `;
  }

  function kebabMenu(){
    return `
      <div class="cmtitem__kebab">
        <button class="kebab" data-kebab type="button">⋯</button>
        <div class="cmtitem__menu">
          <button class="menu__item" data-edit>Редагувати</button>
          <button class="menu__item menu__item--danger" data-delete>Видалити</button>
        </div>
      </div>
    `;
  }

  function ensureModal(){
    let modal = document.querySelector(".cmodal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.className = "cmodal";
    modal.innerHTML = `
      <div class="cmodal__dialog">
        <div class="cmodal__head">
          <div class="cmodal__title">Коментарі</div>
          <button class="cmodal__close" data-close-modal type="button">✕</button>
        </div>
        <div class="cmodal__body">
          <div class="cmodal__toast" role="alert" aria-live="assertive"></div>
          <form class="cmodal__form">
            <textarea rows="3" placeholder="Напишіть коментар..."></textarea>
            <div class="cmodal__actions">
              <button class="btn btn--primary" type="submit">Надіслати</button>
            </div>
          </form>
          <div class="cmodal__list"></div>
        </div>
      </div>`;
    document.body.appendChild(modal);
    return modal;
  }

  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-open-comments]");
    if (btn) {
      e.preventDefault();
      const postId = btn.dataset.postId;
      const modal = ensureModal();
      modal.classList.add("is-open");
      modal.dataset.postId = postId;
      modal.querySelector(".cmodal__form textarea").value = "";
      const data = await api({method:"GET", query:{post_id: postId}});
      renderList(modal, data);
      return;
    }

    if (e.target.classList.contains("cmodal") || e.target.closest("[data-close-modal]")) {
      e.preventDefault();
      document.querySelector(".cmodal")?.classList.remove("is-open");
      return;
    }

    const kebab = e.target.closest(".kebab");
    if (kebab && kebab.closest(".cmtitem__kebab")) {
      const menu = kebab.parentElement.querySelector(".cmtitem__menu");
      if (menu) menu.classList.toggle("is-open");
      e.preventDefault();
      return;
    }

    const del = e.target.closest("[data-delete]");
    if (del) {
      const item = del.closest(".cmtitem");
      const cid = item?.dataset.cid;
      if (!cid) return;
      api({method:"POST", body:{action:"delete", id: cid}}).then(res => {
        if (res.ok) item.remove();
      });
      e.preventDefault();
      return;
    }

    const edit = e.target.closest("[data-edit]");
    if (edit) {
      const item = edit.closest(".cmtitem");
      const textEl = item.querySelector(".cmtitem__text");
      const orig = textEl.textContent.trim();
      item.classList.add("is-editing");
      textEl.innerHTML = `
        <textarea class="cmtitem__edit">${orig.replace(/</g,"&lt;")}</textarea>
        <div class="cmtitem__actions">
          <button class="btn btn--primary" data-save>Зберегти</button>
          <button class="btn" data-cancel>Скасувати</button>
        </div>`;
      e.preventDefault();
      return;
    }

    const cancel = e.target.closest("[data-cancel]");
    if (cancel) {
      const modal = document.querySelector(".cmodal");
      api({method:"GET", query:{post_id: modal.dataset.postId}}).then(data => renderList(modal, data));
      e.preventDefault();
      return;
    }

    const save = e.target.closest("[data-save]");
    if (save) {
      const item = save.closest(".cmtitem");
      const cid = item.dataset.cid;
      const val = item.querySelector(".cmtitem__edit").value;
      api({method:"POST", body:{action:"edit", id: cid, text: val}}).then(res => {
        const modal = document.querySelector(".cmodal");
        if (res.ok) {
          api({method:"GET", query:{post_id: modal.dataset.postId}}).then(data => renderList(modal, data));
        } else if (res.error === "forbidden") {
          showToast(modal, "Можна редагувати лише власний коментар.");
        } else if (res.error === "profanity") {
          showToast(modal, "Коментар містить заборонені слова. Будь ласка, відредагуйте текст.");
        }
      });
      e.preventDefault();
      return;
    }

    const showReply = e.target.closest("[data-show-reply]");
    if (showReply) {
      const wrap = showReply.closest(".replies");
      const form = wrap.querySelector(".reply-form");
      form.hidden = !form.hidden;
      if (!form.hidden) {
        const ta = form.querySelector("textarea");
        ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length);
      }
      e.preventDefault();
      return;
    }
    const hideReply = e.target.closest("[data-hide-reply]");
    if (hideReply) {
      const form = hideReply.closest(".reply-form");
      form.hidden = true;
      e.preventDefault();
      return;
    }

    const toggle = e.target.closest("[data-toggle-replies]");
    if (toggle) {
      const wrap = toggle.closest(".replies");
      const list = wrap.querySelector(".reply-list");
      const parentId = wrap.dataset.parentId;
      if (list.hasAttribute("hidden")) {
        api({method:"POST", body:{action:"load_replies", parent_id: parentId}}).then(res => {
          if (res.ok) {
            list.innerHTML = res.replies.map(r => `
              <div class="cmtitem reply" data-cid="${r.id}">
                <div class="cmtitem__avatar">${r.avatar ? `<img src="${r.avatar}">` : `<div class="cmtitem__placeholder">👤</div>`}</div>
                <div class="cmtitem__body">
                  <div class="cmtitem__meta">
                    <a class="cmtitem__author" href="${r.author_url}" target="_blank">@${escapeHtml(r.author)}</a>
                    <span class="cmtitem__date">${escapeHtml(r.created_at)}</span>
                    ${r.is_owner ? kebabMenu() : ``}
                  </div>
                  <div class="cmtitem__text">${escapeHtml(r.text)}</div>
                </div>
              </div>
            `).join("") || `<div class="cmodal__empty">Поки немає відповідей.</div>`;
            list.removeAttribute("hidden");
            toggle.textContent = `Сховати відповіді`;
            toggle.classList.add("link--muted");
          }
        });
      } else {
        list.setAttribute("hidden", "");
        toggle.textContent = `Показати відповіді`;
        toggle.classList.add("link--muted");
      }
      e.preventDefault();
      return;
    }
  });

  document.addEventListener("submit", (e) => {
    const form = e.target.closest(".cmodal__form");
    if (form) {
      e.preventDefault();
      const modal = document.querySelector(".cmodal");
      const postId = modal.dataset.postId;
      const text = form.querySelector("textarea").value.trim();
      if (!text) {
        showToast(modal, "Коментар не може бути порожнім");
        return;
      }
      api({method:"POST", body:{action:"create", post_id: postId, text}}).then(res => {
        if (res.ok) {
          form.querySelector("textarea").value = "";
          api({method:"GET", query:{post_id: postId}}).then(data => renderList(modal, data));
        } else if (res.error === "auth") {
          showToast(modal, "Щоб залишити коментар — увійдіть.");
        } else if (res.error === "profanity") {
          showToast(modal, "Коментар містить заборонені слова. Будь ласка, відредагуйте текст.");
        }
      });
    }
  });

  document.addEventListener("submit", (e) => {
    const rform = e.target.closest(".reply-form");
    if (rform) {
      e.preventDefault();
      const modal = document.querySelector(".cmodal");
      const parentId = rform.dataset.replyParent;
      const text = rform.querySelector("textarea").value.trim();
      if (!text) {
        showToast(modal, "Відповідь не може бути порожня");
        return;
      }
      api({method:"POST", body:{action:"reply", parent_id: parentId, text}}).then(res => {
        if (res.ok) {
          rform.querySelector("textarea").value = "";
          const wrap = document.querySelector(`.replies[data-parent-id="${parentId}"]`);
          const list = wrap.querySelector(".reply-list");
          if (list.hasAttribute("hidden")) wrap.querySelector("[data-toggle-replies]").click();
          list.innerHTML = res.replies.map(r => `
              <div class="cmtitem reply" data-cid="${r.id}">
                <div class="cmtitem__avatar">${r.avatar ? `<img src="${r.avatar}">` : `<div class="cmtitem__placeholder">👤</div>`}</div>
                <div class="cmtitem__body">
                  <div class="cmtitem__meta">
                    <a class="cmtitem__author" href="${r.author_url}" target="_blank">@${escapeHtml(r.author)}</a>
                    <span class="cmtitem__date">${escapeHtml(r.created_at)}</span>
                    ${r.is_owner ? kebabMenu() : ``}
                  </div>
                  <div class="cmtitem__text">${escapeHtml(r.text)}</div>
                </div>
              </div>
          `).join("");
        } else if (res.error === "auth") {
          showToast(modal, "Щоб відповісти — увійдіть.");
        } else if (res.error === "profanity") {
          showToast(modal, "Відповідь містить заборонені слова. Будь ласка, відредагуйте текст.");
        }
      });
    }
  });
})();



