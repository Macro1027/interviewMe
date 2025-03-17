import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import numpy as np
import seaborn as sns
import os

def create_architecture_diagram():
    # Ensure the images directory exists
    os.makedirs('images/architecture', exist_ok=True)
    
    # Set seaborn style
    sns.set(style="whitegrid", context="talk")
    
    # Enable interactive mode
    plt.ion()
    
    # Create figure and axis with a larger figure size
    fig, ax = plt.subplots(figsize=(14, 18), dpi=100)  # Increased overall figure height
    
    # Define colors using seaborn palettes
    palette_pres = sns.color_palette("Blues", n_colors=10)[3]
    palette_int = sns.color_palette("Oranges", n_colors=10)[3]
    palette_ext = sns.color_palette("Greys", n_colors=10)[3]
    palette_app = sns.color_palette("Greens", n_colors=10)[3]
    palette_ai = sns.color_palette("Purples", n_colors=10)[3]
    palette_data = sns.color_palette("YlOrBr", n_colors=10)[3]
    palette_infra = sns.color_palette("Blues_r", n_colors=10)[3]
    
    colors = {
        'presentation': palette_pres,
        'integration': palette_int,
        'external': palette_ext,
        'application': palette_app,
        'ai_core': palette_ai,
        'data': palette_data,
        'infrastructure': palette_infra
    }
    
    # Adjusted layers with increased heights to accommodate components
    layers = [
        {'name': 'PRESENTATION LAYER', 'y': 17, 'height': 3.0, 'color': colors['presentation']},
        {'name': 'INTEGRATION/EXTERNAL LAYER', 'y': 12.5, 'height': 3.5, 'color': colors['integration']},
        {'name': 'APPLICATION LAYER', 'y': 8.5, 'height': 3.0, 'color': colors['application']},
        {'name': 'AI CORE LAYER', 'y': 5, 'height': 3.0, 'color': colors['ai_core']},
        {'name': 'DATA LAYER', 'y': 2, 'height': 3.0, 'color': colors['data']},
        {'name': 'INFRASTRUCTURE LAYER', 'y': 0, 'height': 2.0, 'color': colors['infrastructure']}
    ]
    
    # Draw layers with adjusted heights
    for layer in layers:
        rect = patches.Rectangle((1, layer['y']), 12, layer['height'], linewidth=1, 
                                edgecolor='black', facecolor=layer['color'], alpha=0.8)
        ax.add_patch(rect)
        ax.text(7, layer['y'] + layer['height']/2, layer['name'], ha='center', va='center', 
                fontsize=12, fontweight='bold')
    
    # Draw connecting arrows with improved styling
    arrow_props = dict(arrowstyle='->', linewidth=1.5, color='black', connectionstyle='arc3,rad=0.1')
    # Draw arrows connecting the centers of each layer
    for i in range(len(layers) - 1):
        start_y = layers[i]['y'] 
        end_y = layers[i+1]['y'] + layers[i+1]['height']
        ax.annotate('', xy=(7, end_y), xytext=(7, start_y), arrowprops=arrow_props)
    
    # Adjust component positions to match new layer positions
    components = [
        # Presentation Layer (adjusted y-positions)
        {'name': 'Web Application\n(React + Redux)', 'x': 3, 'y': 19, 'layer': 'presentation'},
        {'name': 'Mobile Application\n(React Native/Flutter)', 'x': 7, 'y': 19, 'layer': 'presentation'},
        {'name': 'Admin Dashboard', 'x': 11, 'y': 19, 'layer': 'presentation'},
        {'name': 'User Interface Components', 'x': 3, 'y': 18, 'layer': 'presentation'},
        {'name': 'Interview Interface', 'x': 7, 'y': 18, 'layer': 'presentation'},
        {'name': 'Feedback Dashboard', 'x': 11, 'y': 18, 'layer': 'presentation'},
        
        # Integration Layer - Left side
        {'name': 'API Gateway', 'x': 3.5, 'y': 15, 'layer': 'integration'},
        {'name': 'Auth Service', 'x': 3.5, 'y': 14, 'layer': 'integration'},
        {'name': 'WebSocket API', 'x': 3.5, 'y': 13, 'layer': 'integration'},
        
        # External Services - Right side
        {'name': 'Calendar Services', 'x': 10.5, 'y': 15, 'layer': 'external'},
        {'name': 'Identity Providers', 'x': 10.5, 'y': 14, 'layer': 'external'},
        {'name': 'Payment Gateways', 'x': 10.5, 'y': 13, 'layer': 'external'},
        
        # Application Layer - Spread out more
        {'name': 'User Management', 'x': 3, 'y': 10.5, 'layer': 'application'},
        {'name': 'Interview Scheduler', 'x': 7, 'y': 10.5, 'layer': 'application'},
        {'name': 'Feedback Engine', 'x': 11, 'y': 10.5, 'layer': 'application'},
        {'name': 'Analytics Service', 'x': 3, 'y': 9.5, 'layer': 'application'},
        {'name': 'Question Generator', 'x': 7, 'y': 9.5, 'layer': 'application'},
        {'name': 'Recording Service', 'x': 11, 'y': 9.5, 'layer': 'application'},
        
        # AI Core Layer - Spread out more
        {'name': 'Speech Recognition', 'x': 3, 'y': 7, 'layer': 'ai_core'},
        {'name': 'NLP & Dialogue', 'x': 7, 'y': 7, 'layer': 'ai_core'},
        {'name': 'Voice Synthesis', 'x': 11, 'y': 7, 'layer': 'ai_core'},
        {'name': 'Emotion Analysis', 'x': 3, 'y': 6, 'layer': 'ai_core'},
        {'name': 'Multilingual Support', 'x': 7, 'y': 6, 'layer': 'ai_core'},
        {'name': 'Bias Detection', 'x': 11, 'y': 6, 'layer': 'ai_core'},
        
        # Data Layer - Spread out more
        {'name': 'User Database\n(PostgreSQL)', 'x': 3, 'y': 4, 'layer': 'data'},
        {'name': 'Interview Database\n(MongoDB)', 'x': 7, 'y': 4, 'layer': 'data'},
        {'name': 'Question Database\n(MongoDB)', 'x': 11, 'y': 4, 'layer': 'data'},
        {'name': 'Analytics Database', 'x': 3, 'y': 3, 'layer': 'data'},
        {'name': 'Model Storage\n(S3/Azure)', 'x': 7, 'y': 3, 'layer': 'data'},
        {'name': 'Media Storage\n(S3/Azure)', 'x': 11, 'y': 3, 'layer': 'data'},
        
        # Infrastructure Layer - Spread out more
        {'name': 'Container\nOrchestration', 'x': 3, 'y': 1.3, 'layer': 'infrastructure'},
        {'name': 'Load Balancing', 'x': 7, 'y': 1.3, 'layer': 'infrastructure'},
        {'name': 'Auto-scaling', 'x': 11, 'y': 1.3, 'layer': 'infrastructure'},
        {'name': 'Monitoring', 'x': 3, 'y': 0.5, 'layer': 'infrastructure'},
        {'name': 'Logging', 'x': 7, 'y': 0.5, 'layer': 'infrastructure'},
        {'name': 'Security', 'x': 11, 'y': 0.5, 'layer': 'infrastructure'},
    ]
    
    # Add component boxes with increased spacing and size
    for comp in components:
        color = colors[comp['layer']]
        # Make boxes slightly bigger and more spread out
        rect = patches.FancyBboxPatch((comp['x']-1.5, comp['y']-0.3), 3, 0.6, 
                                    boxstyle=patches.BoxStyle("Round", pad=0.3),
                                    linewidth=1, edgecolor='black', 
                                    facecolor=color, alpha=0.6)
        ax.add_patch(rect)
        ax.text(comp['x'], comp['y'], comp['name'], ha='center', va='center', 
                fontsize=8, fontweight='bold')
    
    # Add title with seaborn style
    plt.suptitle('AI INTERVIEW SIMULATION PLATFORM', fontsize=16, fontweight='bold')
    
    # Set axis properties with expanded limits
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.5, 20.5)  # Expanded axis limits
    ax.axis('off')
    
    # Apply seaborn despine for clean look
    sns.despine(left=True, bottom=True, right=True, top=True)
    
    # Add instructions text for zooming
    plt.figtext(0.5, 0.01, 
                "Use the navigation toolbar to zoom and pan. Press 'h' for help.", 
                ha='center', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])  # Adjust for title and footer text
    
    # Save the diagram to the dedicated images directory
    image_path = os.path.join('images', 'architecture', 'ai_interview_architecture.png')
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    print(f"Diagram saved as '{image_path}'")
    
    # Show plot with interactive controls enabled
    # This will display with the default matplotlib toolbar for zooming
    plt.show()

def save_custom_diagram(name, title=None, **kwargs):
    """
    Function to save any generated diagrams to the proper directory structure.
    
    Parameters:
    - name: Name of the diagram file (without extension)
    - title: Optional title for the diagram
    - **kwargs: Additional parameters to pass to savefig
    
    Returns:
    - Path to the saved image
    """
    # Ensure the images directory exists
    os.makedirs('images/architecture', exist_ok=True)
    
    # Create the full path
    image_path = os.path.join('images', 'architecture', f"{name}.png")
    
    # If we have a current figure, save it
    if plt.get_fignums():
        if title:
            plt.suptitle(title, fontsize=16, fontweight='bold')
        
        # Save with high quality
        dpi = kwargs.get('dpi', 300)
        plt.savefig(image_path, dpi=dpi, bbox_inches='tight')
        print(f"Diagram saved as '{image_path}'")
    
    return image_path

# Create the diagram when script is run
if __name__ == "__main__":
    create_architecture_diagram()
