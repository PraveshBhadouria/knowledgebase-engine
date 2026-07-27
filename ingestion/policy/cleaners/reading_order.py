from statistics import median


COLUMN_THRESHOLD = 80


def reconstruct_reading_order(pages):
    """
    Reconstruct logical reading order.

    Output format remains identical to input.
    Only the order of elements changes.
    """

    print("\n" + "=" * 120)
    print("READING ORDER RECONSTRUCTION STARTED")
    print("=" * 120)

    output_pages = []

    total_single = 0
    total_double = 0

    for page in pages:

        print("\n" + "=" * 120)
        print(f"PAGE {page['page']}")
        print("=" * 120)

        elements = page["elements"]

        if not elements:

            print("NO ELEMENTS FOUND")
            output_pages.append(page)
            continue

        page_width = page["width"]
        center = page_width / 2

        print(f"PAGE WIDTH       : {round(page_width,2)}")
        print(f"PAGE CENTER      : {round(center,2)}")
        print(f"TOTAL ELEMENTS   : {len(elements)}")

        # =====================================================
        # BEFORE SORTING
        # =====================================================

        print("\nFIRST 10 ELEMENTS (RAW ORDER)")
        print("-" * 100)

        for i, element in enumerate(elements[:10], start=1):

            print(
                f"{i:02d}. "
                f"X={round(element['bbox'][0],1):>6} "
                f"Y={round(element['bbox'][1],1):>6} "
                f"{element['text'][:80]}"
            )

        left_column = []
        right_column = []

        # =====================================================
        # COLUMN SPLIT
        # =====================================================

        for element in elements:

            x0 = element["bbox"][0]

            if x0 < center - COLUMN_THRESHOLD:

                left_column.append(element)

            else:

                right_column.append(element)

        print("\nCOLUMN ANALYSIS")
        print("-" * 100)

        print(
            f"LEFT COLUMN ELEMENTS  : {len(left_column)}"
        )

        print(
            f"RIGHT COLUMN ELEMENTS : {len(right_column)}"
        )

        # =====================================================
        # SORT COLUMNS
        # =====================================================

        left_column.sort(
            key=lambda x: (
                round(x["bbox"][1], 1),
                round(x["bbox"][0], 1),
            )
        )

        right_column.sort(
            key=lambda x: (
                round(x["bbox"][1], 1),
                round(x["bbox"][0], 1),
            )
        )

        # =====================================================
        # DETECT LAYOUT
        # =====================================================

        use_two_columns = False

        if left_column and right_column:

            left_x = median(
                item["bbox"][0]
                for item in left_column
            )

            right_x = median(
                item["bbox"][0]
                for item in right_column
            )

            distance = abs(right_x - left_x)

            print(
                f"\nLEFT MEDIAN X   : {round(left_x,2)}"
            )

            print(
                f"RIGHT MEDIAN X  : {round(right_x,2)}"
            )

            print(
                f"COLUMN DISTANCE : {round(distance,2)}"
            )

            if distance > 150:

                use_two_columns = True

        # =====================================================
        # BUILD READING ORDER
        # =====================================================

        if use_two_columns:

            ordered = left_column + right_column

            total_double += 1

            print("\nLAYOUT DETECTED : TWO COLUMN")

        else:

            ordered = sorted(
                elements,
                key=lambda x: (
                    round(x["bbox"][1], 1),
                    round(x["bbox"][0], 1),
                )
            )

            total_single += 1

            print("\nLAYOUT DETECTED : SINGLE COLUMN")

        # =====================================================
        # FINAL ORDER
        # =====================================================

        print("\nFIRST 15 ELEMENTS (FINAL ORDER)")
        print("-" * 100)

        for i, element in enumerate(
            ordered[:15],
            start=1,
        ):

            print(
                f"{i:02d}. "
                f"X={round(element['bbox'][0],1):>6} "
                f"Y={round(element['bbox'][1],1):>6} "
                f"{element['text'][:80]}"
            )

        output_pages.append(
            {
                **page,
                "elements": ordered,
            }
        )

        print("\nPAGE SUMMARY")
        print("-" * 100)

        print(
            f"Original Elements : {len(elements)}"
        )

        print(
            f"Ordered Elements  : {len(ordered)}"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)
    print("READING ORDER SUMMARY")
    print("=" * 120)

    print(
        f"TOTAL PAGES        : {len(output_pages)}"
    )

    print(
        f"SINGLE COLUMN      : {total_single}"
    )

    print(
        f"TWO COLUMN         : {total_double}"
    )

    print("=" * 120)
    print("READING ORDER RECONSTRUCTION COMPLETE")
    print("=" * 120)

    return output_pages