# Implementation Plan: PC Parts Category Feature

## Overview

This feature introduces a mandatory top-level "PC Parts" category that is automatically created during database migrations. The dashboard will be modified to display only items from the "PC Parts" category, showing them with the format "Subcategory: Item Name" for items in subcategories.

## Tasks

- [-] 1. Create data migration for PC Parts category
  - [x] 1.1 Create migration file `categories/migrations/0003_create_pc_parts_category.py`
    - Add migration that creates the "PC Parts" category if it doesn't exist
    - Handle idempotency by checking for existing category before creation
    - Set `is_active=True` and `parent=None` (root category)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 1.2 Write property test for category creation idempotency
    - **Property 1: PC Parts category creation is idempotent**
    - **Validates: Requirements 1.1, 1.2, 1.5**
    - Run migration multiple times and verify only one "PC Parts" category exists
  
  - [ ]* 1.3 Write unit tests for migration
    - Test migration creates category when it doesn't exist
    - Test migration does not create duplicate when category exists
    - Test migration handles concurrent execution safely
    - _Requirements: 1.1, 1.2_

- [x] 2. Modify DashboardView to filter PC Parts items
  - [x] 2.1 Update `authentication/views.py` DashboardView
    - Import Category model from categories app
    - Find the "PC Parts" category (root level, no parent)
    - Filter inventory items to only include those in PC Parts category (including subcategories)
    - Calculate statistics for PC Parts items only (replace current global counts)
    - Handle case where PC Parts category doesn't exist gracefully
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 2.2 Write property test for dashboard filtering
    - **Property 2: Dashboard displays items from PC Parts category**
    - **Validates: Requirements 3.1, 3.3**
    - Generate users with items in various categories, verify dashboard returns only PC Parts items
  
  - [ ]* 2.3 Write unit tests for dashboard view modifications
    - Test dashboard shows items from PC Parts category only
    - Test dashboard handles missing PC Parts category gracefully
    - Test dashboard shows correct item count and stats for PC Parts
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Update dashboard template for new display format
  - [x] 3.1 Update `templates/dashboard.html`
    - Change section title from "Recent Inventory Items" to "PC Parts Items"
    - Update empty state message to reflect PC Parts
    - Update tip message to mention PC Parts organization
    - _Requirements: 3.3, 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 3.2 Write unit tests for display format logic
    - Test items with subcategory show "Subcategory: Name" format
    - Test items directly under PC Parts show only name
    - Test nested subcategories show immediate parent name
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Create test for complete workflow
  - [ ] 5.1 Write integration test for complete workflow
    - Run migrations to create "PC Parts" category
    - Create test user with items in PC Parts category and other categories
    - Verify dashboard displays only PC Parts items with correct format
    - Verify statistics reflect only PC Parts items
    - _Requirements: 1.1, 3.1, 4.1_
  
  - [ ]* 5.2 Write integration test for soft-delete behavior
    - Create items in PC Parts category
    - Soft-delete items
    - Verify items don't appear on dashboard
    - _Requirements: 5.2_

- [x] 6. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (Property 1, 2)
- Unit tests validate specific examples and edge cases
- The design document includes additional properties (3, 4, 5, 6) that should be tested if time permits
- Python will be used for all implementation tasks, following Django best practices