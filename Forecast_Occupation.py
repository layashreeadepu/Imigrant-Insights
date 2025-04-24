import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from datetime import datetime
import os

def forecast_occupations(data, occupation_categories=None, countries=None, forecast_years=5, 
                        show_combined=True, save_path=None, degree=2):
    """
    Generate 5-year forecasts for selected occupation categories and countries.
    
    Parameters:
    -----------
    data : pandas DataFrame
        The dataset containing immigration data with columns:
        'Year', 'Region', 'Group', 'Subgroup', 'Total'
    
    occupation_categories : list or None
        List of occupation categories to include. If None, all are included.
        Example: ['Management, professional, and related occupations', 'Service occupations']
    
    countries : list or None
        List of countries to include. If None, all are included.
    
    forecast_years : int
        Number of years to forecast ahead (default: 5)
    
    show_combined : bool
        Whether to show a combined plot of all forecasts (default: True)
    
    save_path : str or None
        Directory path to save plots. If None, plots are not saved.
    
    degree : int
        Degree of polynomial regression (default: 2)
    
    Returns:
    --------
    dict
        Dictionary containing forecast dataframes for each occupation category
    """
    # Filter for occupation data
    data = data.copy()
    occupation_data = data[data['Group'] == 'Occupation'].copy()
    
    # Convert year to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(occupation_data['Year']):
        occupation_data['Year'] = pd.to_datetime(occupation_data['Year'], format='%Y')
    
    # Filter for specified countries
    if countries is not None:
        occupation_data = occupation_data[occupation_data['Region'].isin(countries)]
    
    # Normalize occupation names
    occupation_data['Occupation_Category'] = occupation_data['Subgroup'].str.strip()
    
    # Filter for specified occupation categories
    if occupation_categories is None:
        occupation_categories = occupation_data['Occupation_Category'].unique()
    else:
        occupation_data = occupation_data[occupation_data['Occupation_Category'].isin(occupation_categories)]
    
    # Check if we have data
    if occupation_data.empty:
        raise ValueError("No data found for the specified filters")
    
    # Create output directory if needed
    if save_path is not None:
        os.makedirs(save_path, exist_ok=True)
    
    # Dictionary to store forecast results
    forecasts = {}
    
    # Set up for combined plot
    if show_combined:
        plt.figure(figsize=(12, 8))
        
    # Define unique color map for consistent colors
    num_categories = len(occupation_categories)
    colors = plt.cm.viridis(np.linspace(0, 1, num_categories))
    
    # Set current year for labeling
    current_year = datetime.now().year
    
    # Process each occupation category
    for idx, category in enumerate(occupation_categories):
        try:
            # Filter for this category
            category_data = occupation_data[occupation_data['Occupation_Category'] == category]
            
            # Group by year and sum
            yearly_data = category_data.groupby(category_data['Year'].dt.year)['Total'].sum()
            
            # Create time series
            ts = pd.Series(yearly_data.values, index=pd.date_range(
                start=f'{yearly_data.index[0]}-01-01',
                periods=len(yearly_data),
                freq='AS'
            ))
            
            # Prepare data for regression
            years_array = np.array([d.year for d in ts.index]).reshape(-1, 1)
            values = ts.values
            
            # Create polynomial features
            poly = PolynomialFeatures(degree=degree)
            X_poly = poly.fit_transform(years_array)
            
            # Fit polynomial regression
            model = LinearRegression()
            model.fit(X_poly, values)
            
            # Prepare forecast data
            last_year = years_array[-1][0]
            forecast_years_array = np.array(range(min(years_array)[0], last_year + forecast_years + 1)).reshape(-1, 1)
            forecast_index = pd.date_range(
                start=f'{forecast_years_array[0][0]}-01-01', 
                periods=len(forecast_years_array), 
                freq='AS'
            )
            
            # Generate forecast
            X_poly_future = poly.transform(forecast_years_array)
            forecast_values = model.predict(X_poly_future)
            
            # Get confidence intervals
            ols_model = sm.OLS(values, X_poly).fit()
            predictions = ols_model.get_prediction(X_poly_future)
            ci = predictions.conf_int(alpha=0.05)
            
            # Make sure no negative values
            forecast_values = np.clip(forecast_values, 0, None)
            lower_ci = np.clip(ci[:, 0], 0, None)
            upper_ci = np.clip(ci[:, 1], 0, None)
            
            # Split into historical and forecast
            historical_end_idx = len(years_array) - 1
            historical_years = forecast_index[:historical_end_idx + 1]
            future_years = forecast_index[historical_end_idx:]
            historical_values = forecast_values[:historical_end_idx + 1]
            future_values = forecast_values[historical_end_idx:]
            
            # Store results
            forecast_df = pd.DataFrame({
                'Date': forecast_index,
                'Year': [d.year for d in forecast_index],
                'Forecast': forecast_values,
                'Lower_CI': lower_ci,
                'Upper_CI': upper_ci,
                'Is_Forecast': [i > historical_end_idx for i in range(len(forecast_index))]
            })
            
            forecasts[category] = forecast_df
            
            # Create individual plot for this category
            plt.figure(figsize=(14, 8))
            
            # Plot actual data
            plt.plot(ts.index, ts.values, 'o-', color=colors[idx], label='Historical Data', markersize=6)
            
            # Plot historical fit
            plt.plot(
                historical_years, historical_values, 
                '--', color='lightgray', linewidth=2, 
                label='Polynomial Fit (Historical)'
            )
            
            # Plot forecast
            plt.plot(
                future_years, future_values, 
                '-', color=colors[idx], linewidth=3, 
                label='Forecast'
            )
            
            # Plot confidence interval
            plt.fill_between(
                forecast_index[historical_end_idx:], 
                lower_ci[historical_end_idx:], 
                upper_ci[historical_end_idx:], 
                color=colors[idx], alpha=0.2, 
                label='95% Confidence Interval'
            )
            
            # Add forecast start line
            plt.axvline(
                x=historical_years[-1], 
                color='gray', linestyle='--', 
                alpha=0.7
            )
            
            # Add annotation for forecast start
            plt.text(
                historical_years[-1], 
                plt.ylim()[0] + (plt.ylim()[1] - plt.ylim()[0]) * 0.05,
                'Forecast Start', rotation=90, verticalalignment='bottom'
            )
            
            # Format plot
            plt.title(f'5-Year Forecast for {category}', fontsize=16)
            plt.xlabel('Year', fontsize=14)
            plt.ylabel('Number of Immigrants', fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.legend(loc='best')
            
            # Add R-squared to plot
            plt.figtext(
                0.15, 0.15, 
                f"R² = {ols_model.rsquared:.3f}", 
                bbox=dict(facecolor='white', alpha=0.8)
            )
            
            plt.tight_layout()
            
            # Save if requested
            if save_path:
                safe_name = category.replace('/', '_').replace(':', '').replace(',', '').replace(' ', '_')
                plt.savefig(f"{save_path}/{safe_name}_forecast.png", dpi=300, bbox_inches='tight')
            
            plt.show()
            
            # Add to combined plot if requested
            if show_combined:
                plt.plot(
                    future_years, 
                    future_values, 
                    '-', color=colors[idx], 
                    linewidth=2, label=category.split(',')[0]
                )
            
            print(f"Forecast completed for: {category} | R²: {ols_model.rsquared:.3f}")
            
        except Exception as e:
            print(f"Error processing {category}: {e}")
    
    # Finalize combined plot
    if show_combined and len(forecasts) > 0:
        plt.title('Comparative 5-Year Forecast by Occupation Category', fontsize=16)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Projected Number of Immigrants', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.axvline(x=pd.Timestamp(f"{current_year}-01-01"), color='gray', linestyle='--')
        plt.text(
            pd.Timestamp(f"{current_year}-01-01"), 
            plt.ylim()[0] + (plt.ylim()[1] - plt.ylim()[0]) * 0.05,
            'Current Year', rotation=90, verticalalignment='bottom'
        )
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}/combined_forecast.png", dpi=300, bbox_inches='tight')
        
        plt.show()
    
    return forecasts
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate occupation forecasts')
    parser.add_argument('--data', required=True, help='Path to the data file (.csv or .xlsx)')
    parser.add_argument('--occupations', nargs='+', help='Occupation categories to forecast (if not specified, all will be used)')
    parser.add_argument('--countries', nargs='+', help='Countries to filter (if not specified, all will be used)')
    parser.add_argument('--years', type=int, default=5, help='Number of years to forecast (default: 5)')
    parser.add_argument('--output', help='Directory to save plots')
    
    args = parser.parse_args()
    
    # Load data
    if args.data.endswith('.csv'):
        df = pd.read_csv(args.data)
    elif args.data.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(args.data)
    else:
        raise ValueError("Data file must be .csv or .xlsx/.xls")
    
    # Run forecast
    forecasts = forecast_occupations(
        data=df,
        occupation_categories=args.occupations,
        countries=args.countries,
        forecast_years=args.years,
        show_combined=True,
        save_path=args.output
    )
    
    print(f"Forecasting complete. Generated forecasts for {len(forecasts)} occupation categories.")

# Example usage:
"""
# Define key occupation categories
occupation_categories = [
    'Management, professional, and related occupations',
    'Service occupations',
    'Sales and office occupations',
    'Construction, extraction, maintenance and repair occupations',
    'Production, transportation, and material moving occupations',
    'Farming, fishing, and forestry occupations',
    'Military'
]

# Generate forecasts for all categories
forecasts = forecast_occupations(
    data=df_common,
    occupation_categories=occupation_categories,
    countries=['India', 'China', 'Mexico'],  # Specific countries or None for all
    save_path='forecast_plots'
)

# Access forecast data for a specific category
management_forecast = forecasts['Management, professional, and related occupations']
print(management_forecast.tail())
"""