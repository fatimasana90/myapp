from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, PasswordField,SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange,Optional
from flask_wtf.file import FileField, FileAllowed


class ShopForm(FlaskForm):
    name = StringField('نام کافه و رستوران', validators=[DataRequired(), Length(max=100)])
    address = StringField('آدرس', validators=[DataRequired(), Length(max=200)])
    contact_info = StringField('اطلاعات تماس', validators=[Length(max=100)])
    status = StringField('وضعیت', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('ثبت')


class ProductForm(FlaskForm):
    name = StringField('نام محصول', validators=[DataRequired(), Length(max=100)])
    stock = IntegerField('موجودی', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('قیمت', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('دسته‌بندی', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('ثبت')


class AddProductForm(FlaskForm):
    name = StringField('نام محصول', validators=[DataRequired(), Length(max=100)])
    stock = IntegerField('موجودی', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('قیمت', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('دسته‌بندی', validators=[DataRequired(), Length(max=50)])
    image = FileField('تصویر محصول', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'فقط فایل‌های تصویری مجاز هستند')
    ])
    submit = SubmitField('افزودن محصول')


class RegisterForm(FlaskForm):
    email = StringField('ایمیل', validators=[
        DataRequired(), Email(), Length(max=150)
    ])
    password = PasswordField('رمز عبور', validators=[
        DataRequired(), Length(min=6)
    ])
    confirm = PasswordField('تایید رمز عبور', validators=[
        DataRequired(), EqualTo('password', message='رمزها یکسان نیستند')
    ])
    submit = SubmitField('ثبت‌نام')


class LoginForm(FlaskForm):
    email = StringField('ایمیل', validators=[
        DataRequired(), Email(), Length(max=150)
    ])
    password = PasswordField('رمز عبور', validators=[
        DataRequired()
    ])
    submit = SubmitField('ورود')

class UpdateProductForm(FlaskForm):
    name = StringField('نام محصول', validators=[DataRequired(), Length(max=100)])
    stock = IntegerField('موجودی', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('قیمت', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('دسته‌بندی', validators=[DataRequired(), Length(max=50)])
    image = FileField('تغییر تصویر محصول', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'فقط فایل تصویری مجاز است')
    ])
    submit = SubmitField('ذخیره تغییرات')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('رمز عبور فعلی', validators=[DataRequired()])
    new_password = PasswordField('رمز عبور جدید', validators=[DataRequired(), Length(min=6)])
    confirm_new = PasswordField('تایید رمز عبور جدید', validators=[
        DataRequired(), EqualTo('new_password', message='رمزهای جدید یکسان نیستند')
    ])
    submit = SubmitField('تغییر رمز')

class ProductSearchForm(FlaskForm):
    name = StringField('نام', validators=[Optional()])
    category = StringField('دسته‌بندی', validators=[Optional()])
    min_price = FloatField('حداقل قیمت', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('حداکثر قیمت', validators=[Optional(), NumberRange(min=0)])
    sort_by = SelectField('مرتب‌سازی بر اساس', choices=[
        ('newest', 'جدیدترین'),
        ('price_asc', 'ارزان‌ترین'),
        ('price_desc', 'گران‌ترین'),
        ('stock', 'موجودی')
    ], default='newest')
    submit = SubmitField('جستجو')

