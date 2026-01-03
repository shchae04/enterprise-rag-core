import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join("/");
  const url = `${BACKEND_URL}/api/v1/${path}?${request.nextUrl.searchParams}`;

  const headers: HeadersInit = {};
  const authHeader = request.headers.get("authorization");
  if (authHeader) {
    headers["Authorization"] = authHeader;
  }

  try {
    const response = await fetch(url, { headers });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Backend proxy error:", error);
    return NextResponse.json(
      { error: "Backend request failed", detail: error instanceof Error ? error.message : "Unknown error" },
      { status: 502 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join("/");
  const url = `${BACKEND_URL}/api/v1/${path}`;

  const headers: HeadersInit = {};
  const authHeader = request.headers.get("authorization");
  if (authHeader) {
    headers["Authorization"] = authHeader;
  }

  const contentType = request.headers.get("content-type");

  try {
    let body;
    let fetchHeaders = { ...headers };

    if (contentType?.includes("multipart/form-data")) {
      // For file uploads, don't set Content-Type (browser will set boundary)
      body = await request.formData();
    } else if (contentType?.includes("application/json")) {
      fetchHeaders["Content-Type"] = "application/json";
      body = JSON.stringify(await request.json());
    } else if (contentType?.includes("application/x-www-form-urlencoded")) {
      fetchHeaders["Content-Type"] = "application/x-www-form-urlencoded";
      body = await request.text();
    } else {
      body = await request.text();
    }

    const response = await fetch(url, {
      method: "POST",
      headers: fetchHeaders,
      body,
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Backend proxy error:", error);
    return NextResponse.json(
      { error: "Backend request failed", detail: error instanceof Error ? error.message : "Unknown error" },
      { status: 502 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join("/");
  const url = `${BACKEND_URL}/api/v1/${path}`;

  const headers: HeadersInit = {};
  const authHeader = request.headers.get("authorization");
  if (authHeader) {
    headers["Authorization"] = authHeader;
  }

  try {
    const response = await fetch(url, {
      method: "DELETE",
      headers,
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Backend proxy error:", error);
    return NextResponse.json(
      { error: "Backend request failed", detail: error instanceof Error ? error.message : "Unknown error" },
      { status: 502 }
    );
  }
}
