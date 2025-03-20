from flask import Blueprint, render_template
from app.models import HistoricalData

general_bp = Blueprint('general', __name__)

# About Page
@general_bp.route('/about')
def about():
    return render_template('about.html')

# Historical Data Page
@general_bp.route('/historical')
def historical():
    historical_data = HistoricalData.query.order_by(HistoricalData.date.asc()).all()
    return render_template('historical.html', historical_data=historical_data)
