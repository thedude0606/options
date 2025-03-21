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

## Technology Selections

### Backend
- **Decision**: Python 3.11 with Schwabdev library
- **Rationale**: Schwabdev is a Python wrapper specifically designed for Schwab API and requires Python 3.11+
- **Alternatives Considered**: JavaScript/Node.js with custom API integration, custom Python implementation
- **Consequences**: Leverages existing library capabilities, faster development, but requires specific Python version

### Frontend/Dashboard
- **Decision**: Web-based dashboard using Dash or Streamlit
- **Rationale**: These frameworks provide easy integration with Python backend and built-in data visualization components
- **Alternatives Considered**: React.js, Vue.js
- **Consequences**: Faster development of visualization components, potentially less customization

### Data Storage
- **Decision**: Use local file-based storage initially with option to migrate to database
- **Rationale**: Simplifies initial development while allowing for future scalability
- **Alternatives Considered**: Immediate database implementation
- **Consequences**: Faster initial development, may require migration effort later

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

## Implementation Decisions

### Message Parsing Strategy
- **Decision**: Implement flexible message parsing to handle different Schwab API response formats
- **Rationale**: The Schwab API can return data in different formats depending on the context
- **Alternatives Considered**: Strict parsing expecting a single format
- **Consequences**: More resilient to API changes and variations in response format

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
