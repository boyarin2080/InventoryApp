# Requirements Document: PC Parts Category Feature

## Introduction

The Inventory Management System is a web application for users who repair and resell electronics. Currently, the main dashboard displays "Recent Inventory Items" to all users. This feature adds a mandatory top-level category called "PC Parts" that will be automatically created when the database is initialized or migrated. Instead of showing general recent inventory items, the dashboard will display items specifically from the "PC Parts" category, showing both the subcategory name (e.g., "GPU") and the item name (e.g., "RTX 2060") in the display format.

## Glossary

- **System**: The Inventory Management System web application
- **User**: A registered user who repairs and resells electronics
- **Category**: A classification group for inventory items with hierarchical relationships (parent/children)
- **PC_Parts_Category**: The mandatory top-level category named "PC Parts" that contains subcategories like GPU, CPU, RAM, etc.
- **Inventory_Item**: A product purchased for repair and resale, associated with a category
- **Dashboard**: The main home screen displayed to authenticated users
- **Subcategory**: A category that has a parent category (e.g., "GPU" under "PC Parts")

## Requirements

### Requirement 1: Mandatory PC Parts Category Creation

**User Story:** As a system administrator, I want the "PC Parts" category to be created automatically when the database is initialized, so that the application has a foundational category for organizing computer hardware inventory.

#### Acceptance Criteria

1. WHEN the database is initialized or migrated, THE System SHALL create a root-level category named "PC Parts" if it does not already exist
2. IF the "PC Parts" category already exists, THE System SHALL NOT create a duplicate
3. THE "PC Parts" category SHALL be marked as active (is_active = True) upon creation
4. WHERE database migrations are applied, THE System SHALL verify the existence of the "PC Parts" category and create it if missing
5. THE Creation of the "PC Parts" category SHALL be idempotent (safe to run multiple times)

### Requirement 2: Subcategory Support Under PC Parts

**User Story:** As a user, I want to organize PC Parts inventory items into logical subcategories, so that I can easily find and manage items like GPUs, CPUs, RAM, etc.

#### Acceptance Criteria

1. THE System SHALL allow subcategories to be created under the "PC Parts" category (e.g., "GPU", "CPU", "RAM", "SSD", "Motherboard")
2. WHEN a subcategory is created under "PC Parts", THE System SHALL establish a parent-child relationship
3. WHEN viewing a subcategory, THE System SHALL display its parent category path
4. THE "PC Parts" category SHALL support unlimited levels of subcategory nesting

### Requirement 3: Dashboard Display PC Parts Items

**User Story:** As a user, I want the dashboard to show items from the "PC Parts" category instead of general recent items, so that I can quickly see my PC-related inventory.

#### Acceptance Criteria

1. WHEN the dashboard is loaded, THE System SHALL display items from the "PC Parts" category (including all its subcategories)
2. WHERE no items exist in the "PC Parts" category, THE System SHALL display a message indicating no PC Parts items are available
3. THE Dashboard_SHALL replace the "Recent Inventory Items" section with a "PC Parts Items" section
4. WHEN items from the "PC Parts" category exist, THE System SHALL display them in the dashboard with proper formatting

### Requirement 4: Display Format for Subcategory and Item Name

**User Story:** As a user, I want to see both the subcategory and the item name in the dashboard display, so that I can quickly understand what type of item each entry represents.

#### Acceptance Criteria

1. FOR Each item displayed on the dashboard, THE System SHALL show the subcategory name followed by a colon and the item name (format: "Subcategory: Item Name")
2. EXAMPLE: An item "RTX 2060" in the "GPU" subcategory SHALL be displayed as "GPU: RTX 2060"
3. IF an item's category is "PC Parts" (root level, no subcategory), THE System SHALL display only the item name without a prefix
4. WHERE an item belongs to a subcategory of "PC Parts", THE System SHALL display the immediate subcategory name, not the full path

### Requirement 5: Data Consistency and Integrity

**User Story:** As a developer, I want to ensure data integrity when the "PC Parts" category is created and modified, so that the system remains reliable and predictable.

#### Acceptance Criteria

1. WHEN the "PC Parts" category is deleted, THE System SHALL prevent deletion if items reference it
2. IF the "PC Parts" category is soft-deleted, THE System SHALL handle items referencing it gracefully
3. THE System SHALL validate that the "PC Parts" category name is unique among root categories
4. WHERE category relationships are modified, THE System SHALL enforce hierarchical integrity (no circular references)

### Requirement 6: Migration and Database Setup

**User Story:** As a system administrator, I want the "PC Parts" category to be created during database setup, so that new installations have the necessary foundational category.

#### Acceptance Criteria

1. WHEN database migrations are applied, THE System SHALL check for the existence of the "PC Parts" category and create it if missing
2. THE Creation of the "PC Parts" category SHALL occur during the migration process, not at application startup
3. IF the system is deployed to a new environment, THE System SHALL create the "PC Parts" category automatically
4. WHERE existing data exists, THE System SHALL not modify or delete any existing categories during the creation process

## Appendix: Implementation Notes

### Suggested Approach

1. Create a Django data migration that creates the "PC Parts" category during migration execution
2. Modify the DashboardView to filter inventory items by the "PC Parts" category instead of showing all items
3. Update the dashboard template to display items with the subcategory prefix in the required format
4. Consider adding a signal or post_migrate hook to ensure the category is always present

### Key Files to Modify

- **Migrations**: Create a new data migration for the "PC Parts" category
- **authentication/views.py**: Update DashboardView to fetch items from the "PC Parts" category
- **templates/dashboard.html**: Update the dashboard template to display items with subcategory prefix
