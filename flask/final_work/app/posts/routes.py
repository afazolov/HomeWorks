from datetime import datetime

from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Post
from app.posts import bp
from app.posts.forms import PostForm


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["POSTS_PER_PAGE"]
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("posts/index.html", title="Блог", pagination=pagination)


@bp.route("/post/<int:post_id>")
def detail(post_id: int):
    post = db.session.get(Post, post_id) or abort(404)
    return render_template("posts/detail.html", title=post.title, post=post)


@bp.route("/post/create", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            author=current_user,
        )
        db.session.add(post)
        db.session.commit()
        flash("Пост успешно опубликован!", "success")
        return redirect(url_for("posts.detail", post_id=post.id))
    return render_template("posts/create.html", title="Новый пост", form=form)


@bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id: int):
    post = db.session.get(Post, post_id) or abort(404)
    if post.author_id != current_user.id:
        abort(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Пост обновлён.", "success")
        return redirect(url_for("posts.detail", post_id=post.id))
    return render_template("posts/edit.html", title="Редактировать пост", form=form, post=post)


@bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id: int):
    post = db.session.get(Post, post_id) or abort(404)
    if post.author_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Пост удалён.", "info")
    return redirect(url_for("posts.index"))
