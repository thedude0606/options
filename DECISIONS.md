# Design Decisions

## Architecture Choices

### Authentication Framework
- **Decision**: Use Schwabdev Python wrapper for authentication
- **Rationale**: Schwabdev provides automatic token management and refreshes, simplifying the authentication process
- **Alternatives Considered**: Direct API calls using requests library
- **Consequences**: Dependency on third-party library, but significantly reduces development time and complexity

### Data Retrieval
- **Decision**: Implement separate modules for historical and real-time data
- **Rationale**: Different data types require different handling approaches and update frequencies
- **Alternatives Considered**: Unified data retrieval system
- **Consequences**: More modular code structure, easier to maintain and extend

### Real-time Data Handling
- **Decision**: Implement robust error handling and debug mode in real-time components
- **Rationale**: Improves reliability and makes troubleshooting easier when data flow issues occur
- **Alternatives Considered**: Simpler implementation with less error handling
- **Consequences**: More complex code but significantly improved reliability and easier debugging

### Streaming Architecture
- **Decision**: Implement StreamerSingleton with enhanced thread management and connection handling
- **Rationale**: Prevents multiple connection conflicts when different parts of the application attempt to create streaming connections
- **Alternatives Considered**: Separate streaming instances for different components
- **Consequences**: More reliable streaming with fewer disconnections, but requires careful singleton implementation

### Dashboard Callbacks
- **Decision**: Use allow_duplicate=True parameter for overlapping callback outputs
- **Rationale**: Resolves duplicate callback output errors while maintaining separate callback functions for different triggers
- **Alternatives Considered**: Combining callbacks into a single function
- **Consequences**: Cleaner code organization with separate callbacks for different functionality, while avoiding conflicts

### Analytics Architecture
- **Decision**: Implement modular analytics components for options Greeks and strategy analysis
- **Rationale**: Allows for independent development and testing of different analytics features
- **Alternatives Considered**: Monolithic analytics engine
- **Consequences**: More maintainable code with better separation of concerns, easier to extend with new analytics

### Error Handling Strategy
- **Decision**: Implement comprehensive error handling with detailed logging
- **Rationale**: Provides better visibility into system behavior and makes troubleshooting easier
- **Alternatives Considered**: Minimal error handling with generic error messages
- **Consequences**: More robust application with better user experience during error conditions

## Technology Selections

### Backend
- **Decision**: Python 3.11 with Schwabdev library
- **Rationale**: Schwabdev is a Python wrapper specifically designed for Schwab API and requires Python 3.11+
- **Alternatives Considered**: JavaScript/Node.js with custom API integration, custom Python implementation
- **Consequences**: Leverages existing library capabilities, faster development, but requires specific Python version

### Frontend/Dashboard
- **Decision**: Web-based dashboard using Dash
- **Rationale**: Dash provides easy integration with Python backend and built-in data visualization components
- **Alternatives Considered**: React.js, Vue.js, Streamlit
- **Consequences**: Faster development of visualization components, potentially less customization

### Data Storage
- **Decision**: Use local file-based storage initially with option to migrate to database
- **Rationale**: Simplifies initial development while allowing for future scalability
- **Alternatives Considered**: Immediate database implementation
- **Consequences**: Faster initial development, may require migration effort later

### Machine Learning Framework
- **Decision**: Use hybrid approach with LSTM and Reinforcement Learning models
- **Rationale**: Combines time-series prediction capabilities of LSTM with adaptive decision-making of RL
- **Alternatives Considered**: Pure statistical models, single ML approach
- **Consequences**: More complex implementation but potentially better prediction accuracy for options trading

### Technical Analysis Library
- **Decision**: Use TA-Lib with custom extensions for specialized indicators
- **Rationale**: Provides optimized implementations of common indicators while allowing for custom extensions
- **Alternatives Considered**: Custom implementation of all indicators
- **Consequences**: Faster development with reliable base indicators, with flexibility to add custom ones

### Visualization Components
- **Decision**: Use Plotly for interactive charts and visualizations
- **Rationale**: Provides rich interactive visualization capabilities that integrate well with Dash
- **Alternatives Considered**: Matplotlib, D3.js
- **Consequences**: Better user experience with interactive charts, consistent styling across the application

## Design Patterns

### Observer Pattern
- **Decision**: Use observer pattern for real-time data updates
- **Rationale**: Allows components to subscribe to data changes and update accordingly
- **Consequences**: More responsive UI, better separation of concerns

### Repository Pattern
- **Decision**: Implement repository pattern for data access
- **Rationale**: Abstracts data source details from business logic
- **Consequences**: More maintainable code, easier to change data sources if needed

### Factory Pattern
- **Decision**: Use factory pattern for creating data retrieval components
- **Rationale**: Provides flexibility in creating different types of data retrievers
- **Consequences**: More extensible code, easier to add new data types

### Singleton Pattern
- **Decision**: Use enhanced singleton pattern for streamer management
- **Rationale**: Ensures only one streaming connection is active at a time, preventing conflicts
- **Alternatives Considered**: Global instance or dependency injection
- **Consequences**: More reliable streaming with better resource management

### Strategy Pattern
- **Decision**: Implement strategy pattern for different trading analysis approaches
- **Rationale**: Allows for swapping different analysis algorithms at runtime
- **Alternatives Considered**: Hard-coded analysis logic
- **Consequences**: More flexible system that can adapt to different market conditions

### Facade Pattern
- **Decision**: Implement facade pattern for the DataManager class
- **Rationale**: Provides a simplified interface to the complex subsystem of data retrieval components
- **Alternatives Considered**: Direct access to individual data components
- **Consequences**: Cleaner client code, better encapsulation of implementation details

## Implementation Decisions

### API Parameter Handling
- **Decision**: Use parameter name 'symbol_list' for level_one_equities and level_one_options methods
- **Rationale**: Schwab API requires 'symbol_list' parameter instead of 'symbols' for these specific methods
- **Alternatives Considered**: Using generic parameter handling for all methods
- **Consequences**: More reliable streaming with proper parameter names for each method type

### Handler Registration Strategy
- **Decision**: Implement fallback mechanism for handler registration (add_handler → on_message)
- **Rationale**: Different versions of Schwab API may use different methods for registering message handlers
- **Alternatives Considered**: Using only add_handler method
- **Consequences**: More robust code that works with different versions of the Schwab API

### Method Naming Consistency
- **Decision**: Implement alias methods in DataManager (get_historical_data, get_options_chain)
- **Rationale**: Maintains compatibility with dashboard components that expect these specific method names
- **Alternatives Considered**: Updating all dashboard components to use existing method names
- **Consequences**: Simpler implementation with backward compatibility, avoiding extensive dashboard changes

### Logging and Debugging
- **Decision**: Add comprehensive logging and debug mode to real-time components
- **Rationale**: Makes it easier to identify and fix issues with data flow
- **Alternatives Considered**: Minimal logging with console output
- **Consequences**: Better visibility into system behavior, easier troubleshooting

### Thread Management
- **Decision**: Implement dedicated thread with its own event loop for streaming
- **Rationale**: Prevents asyncio event loop conflicts and ensures proper resource management
- **Alternatives Considered**: Using main application thread or shared event loop
- **Consequences**: More complex implementation but avoids common pitfalls with asyncio and threading

### Multi-timeframe Analysis
- **Decision**: Store and process data at multiple timeframes (15-min, 1-hour, daily)
- **Rationale**: Different trading strategies require different timeframe perspectives
- **Alternatives Considered**: Single timeframe with on-demand aggregation
- **Consequences**: Higher storage requirements but faster analysis and visualization

### Backtesting Framework
- **Decision**: Implement event-driven backtesting with realistic slippage and commission models
- **Rationale**: Provides more accurate performance assessment of trading strategies
- **Alternatives Considered**: Simplified backtesting without market friction
- **Consequences**: More complex implementation but more realistic strategy evaluation

### Environment Configuration
- **Decision**: Use dotenv for environment variable management
- **Rationale**: Provides a secure and flexible way to manage configuration without hardcoding
- **Alternatives Considered**: Configuration files, command-line arguments
- **Consequences**: Better security practices, easier configuration management across environments

### Error Recovery Strategy
- **Decision**: Implement automatic reconnection for streaming data with exponential backoff
- **Rationale**: Improves system resilience during temporary network issues or API disruptions
- **Alternatives Considered**: Manual reconnection or simple retry logic
- **Consequences**: More complex implementation but better user experience with self-healing capabilities
