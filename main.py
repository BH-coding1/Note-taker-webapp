from flask import Flask, render_template, redirect, url_for, request,flash, get_flashed_messages
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float,DATE
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length
import requests
import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

Bootstrap5(app)
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-notes.db'
db = SQLAlchemy(model_class=Base)

db.init_app(app)


class Notes(db.Model):
    id:Mapped[int] = mapped_column(primary_key=True)
    title :Mapped[str] =  mapped_column(String(50))
    content:Mapped[str] = mapped_column(String(300))
    date :Mapped [datetime] = mapped_column(db.DateTime, default=(datetime.date.today()))

with app.app_context():
    db.create_all()

class Myform(FlaskForm):
    title = TextAreaField('Title:',validators=[DataRequired(),Length(min=1,max=50)])
    body = TextAreaField('Body:', validators=[DataRequired(),Length(min=1,max=300)])
    submit = SubmitField('Add')

@app.route('/',methods=['GET','POST'])
def home():
    notes = db.session.execute(db.select(Notes)).scalars().all()
    return render_template('index.html',notes=notes)


@app.route('/add/notes',methods=['GET','POST'])
def add():
    form = Myform()
    if request.method == 'POST'and form.validate_on_submit():
        title_entered_by_user = form.title.data
        content_entered_by_user = form.body.data
        note_to_add = Notes(title=title_entered_by_user,content= content_entered_by_user,date = (datetime.date.today()))
        db.session.add(note_to_add)
        db.session.commit()
        flash("Note CREATED successfully!", "success")
        return redirect(url_for('home'))
    return render_template('add.html', form =form)

@app.route('/delete/notes/<int:id>')
def delete(id):
    note_to_delete = db.get_or_404(Notes,id)
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/update/notes/<int:id>/<title>/<body>',methods=['GET','POST'])
def update(id,title,body):
    form2 = Myform()
    if request.method == 'POST' and form2.validate_on_submit():
        note_to_update = db.get_or_404(Notes,id)
        note_to_update.title = form2.title.data
        note_to_update.content = form2.body.data
        db.session.commit()
        flash("Note UPDATED successfully!", "info")
        return redirect(url_for('home'))
    if request.method == 'GET' :
        form2.title.data = title
        form2.body.data = body
    return render_template('update.html',form = form2,id=id,title=title,body=body)



if __name__=='__main__':
    app.run(debug=True)